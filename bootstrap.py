#!/usr/bin/env python3
"""
Bootstrap script for RooCode project template initialization and migration.
Supports --init (new project setup), --migrate (existing project migration), and --update (safe template updates) modes.
"""

import subprocess
import sys
import shutil
import tempfile
import argparse
import os
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


# --- CONFIGURATION ---
TEMPLATE_DIRS_TO_COPY = [".roo", "scripts", "pages", "docs", "journals"]
MIGRATION_SOURCE_DIRS = ["docs/memory-bank", "docs/memory-bank/user_story"]


def run_command(command, cwd):
    """Run a shell command and return success status."""
    print(f"\n> Running command: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed:\n{result.stderr or result.stdout}")
        return False
    print(result.stdout)
    print("✅ Command succeeded.")
    return True


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        print(f"⚠️  Warning: Could not calculate hash for {file_path}: {e}")
        return ""


def is_file_modified(file_path: Path, original_hash: str) -> bool:
    """Check if a file has been modified by comparing its current hash with the original."""
    if not original_hash:
        return False
    current_hash = calculate_file_hash(file_path)
    return current_hash != original_hash


def copy_template_files(template_path: Path, project_path: Path):
    """Copy template directories to project."""
    print("\n--- Stage 1: Copying/Updating template files ---")
    for dir_name in TEMPLATE_DIRS_TO_COPY:
        source_dir = template_path / dir_name
        target_dir = project_path / dir_name
        
        if not source_dir.is_dir():
            print(f"⚠️  Warning: Template directory '{dir_name}' not found.")
            continue
            
        if target_dir.exists():
            print(f"Updating directory '{dir_name}'...")
            shutil.rmtree(target_dir)
        
        try:
            shutil.copytree(source_dir, target_dir)
            print(f"✅ Directory '{dir_name}' copied successfully.")
        except Exception as e:
            print(f"❌ Error copying '{dir_name}': {e}")


def copy_file_safely(source_file: Path, target_file: Path, file_hashes: Dict[str, str]) -> str:
    """
    Copy a file safely, preserving user modifications.
    Returns status: 'added', 'updated', 'skipped', or 'error'
    """
    try:
        # Create parent directories if they don't exist
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # If target file doesn't exist, simply copy it
        if not target_file.exists():
            shutil.copy2(source_file, target_file)
            return 'added'
        
        # Get relative path for hash lookup
        relative_path = str(source_file.relative_to(source_file.parent.parent))
        
        # Check if we have hash information for this file
        if relative_path in file_hashes:
            original_hash = file_hashes[relative_path]
            # Check if user has modified the file
            if is_file_modified(target_file, original_hash):
                return 'skipped'  # Skip to preserve user changes
        
        # Create backup before overwriting
        backup_path = target_file.with_suffix(target_file.suffix + '.backup')
        shutil.copy2(target_file, backup_path)
        
        # Copy new file
        shutil.copy2(source_file, target_file)
        
        # Remove backup if copy was successful
        if backup_path.exists():
            backup_path.unlink()
        
        return 'updated'
    except Exception as e:
        print(f"❌ Error copying file {source_file} to {target_file}: {e}")
        return 'error'


def update_template_files(template_path: Path, project_path: Path) -> Dict[str, int]:
    """
    Update template files in an existing project safely.
    Only adds missing files or updates unmodified files.
    Returns a dictionary with statistics about the update operation.
    """
    print("\n--- Stage 1: Updating template files safely ---")
    
    # Statistics tracking
    stats = {
        'added': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    # Try to load file hashes from previous run (if available)
    hashes_file = project_path / '.roo' / '.template_hashes.json'
    file_hashes = {}
    if hashes_file.exists():
        try:
            with open(hashes_file, 'r') as f:
                file_hashes = json.load(f)
        except Exception as e:
            print(f"⚠️  Warning: Could not load template hashes: {e}")
    
    # Process each template directory
    for dir_name in TEMPLATE_DIRS_TO_COPY:
        source_dir = template_path / dir_name
        target_dir = project_path / dir_name
        
        if not source_dir.is_dir():
            print(f"⚠️  Warning: Template directory '{dir_name}' not found.")
            continue
        
        print(f"\n📁 Processing directory: {dir_name}")
        
        # Walk through all files in the source directory
        for source_file in source_dir.rglob('*'):
            if source_file.is_file():
                # Calculate the relative path from the source directory
                relative_path = source_file.relative_to(source_dir)
                target_file = target_dir / relative_path
                
                # Copy file safely
                status = copy_file_safely(source_file, target_file, file_hashes)
                
                # Update statistics
                if status == 'added':
                    print(f"  ✅ Added new file: {relative_path}")
                    stats['added'] += 1
                elif status == 'updated':
                    print(f"  🔄 Updated file: {relative_path}")
                    stats['updated'] += 1
                elif status == 'skipped':
                    print(f"  ⏭️  Skipped modified file: {relative_path}")
                    stats['skipped'] += 1
                elif status == 'error':
                    stats['errors'] += 1
    
    # Create/update hash file with current template file hashes
    try:
        new_hashes = {}
        for dir_name in TEMPLATE_DIRS_TO_COPY:
            source_dir = template_path / dir_name
            if source_dir.is_dir():
                for file_path in source_dir.rglob('*'):
                    if file_path.is_file():
                        relative_path = str(file_path.relative_to(template_path))
                        new_hashes[relative_path] = calculate_file_hash(file_path)
        
        # Save hashes for future updates
        hashes_dir = project_path / '.roo'
        hashes_dir.mkdir(exist_ok=True)
        with open(hashes_file, 'w') as f:
            json.dump(new_hashes, f, indent=2)
    except Exception as e:
        print(f"⚠️  Warning: Could not save template hashes: {e}")
    
    return stats


def migrate_existing_docs(project_path: Path):
    """Migrate existing documentation to pages/ directory."""
    print("\n--- Stage 2: Migrating existing documentation to pages/ ---")
    target_pages_dir = project_path / "pages"
    target_pages_dir.mkdir(exist_ok=True)
    migrated_count = 0
    
    for source_rel_path in MIGRATION_SOURCE_DIRS:
        source_dir = project_path / source_rel_path
        if not source_dir.is_dir():
            print(f"ℹ️  Migration source directory not found, skipping: {source_rel_path}")
            continue
            
        print(f"Scanning '{source_rel_path}'...")
        for file_path in source_dir.glob("*.md"):
            target_file_path = target_pages_dir / file_path.name
            if target_file_path.exists():
                print(f"  - ⚠️  File '{file_path.name}' already exists in pages/. Skipping.")
            else:
                try:
                    shutil.move(str(file_path), str(target_file_path))
                    print(f"  - ✅ Moved file: {file_path.name}")
                    migrated_count += 1
                except Exception as e:
                    print(f"  - ❌ Error moving '{file_path.name}': {e}")
    
    print(f"\nTotal files migrated: {migrated_count}")


def create_symlinks_in_pages(project_path: Path):
    """Create symbolic links in pages/ from .roo/ for rules and commands."""
    print("\n--- Stage 3: Creating symbolic links in pages/ ---")
    
    pages_dir = project_path / "pages"
    pages_dir.mkdir(exist_ok=True)
    
    source_dirs = {
        "rules": project_path / ".roo" / "rules",
        "commands": project_path / ".roo" / "commands"
    }

    for link_type, source_dir in source_dirs.items():
        if not source_dir.is_dir():
            print(f"⚠️  Source directory not found, skipping: {source_dir}")
            continue
        
        for source_file in source_dir.glob("*.md"):
            # Create link name preserving prefixes and original name
            # For example: "01-quality_guideline.md" -> "rules.01-quality-guideline.md"
            link_name = f"{link_type}.{source_file.stem.replace('_', '-')}.md"
            link_path = pages_dir / link_name

            if link_path.exists() or link_path.is_symlink():
                link_path.unlink()

            try:
                os.symlink(str(source_file.resolve()), str(link_path.resolve()))
                print(f"✅ Created link: '{link_path}' -> '{source_file}'")
            except OSError as e:
                print(f"❌ Error creating link for '{source_file.name}': {e}")
                print("ℹ️  On Windows, creating symbolic links may require running the script as Administrator.")
            except Exception as e:
                print(f"❌ Unknown error creating link for '{source_file.name}': {e}")


def init_project(project_root: Path, template_path: Path):
    """
    Initialize a new project by copying template files and setting up the structure.
    This is the --init mode implementation.
    """
    print("\n--- 🚀 Initializing new project with RooCode template ---")
    
    # Check if target directories already exist
    existing_dirs = []
    for dir_name in TEMPLATE_DIRS_TO_COPY:
        target_dir = project_root / dir_name
        if target_dir.exists():
            existing_dirs.append(dir_name)
    
    if existing_dirs:
        print(f"⚠️  The following directories already exist: {', '.join(existing_dirs)}")
        print("   They will be overwritten with template files.")
        response = input("Do you want to continue? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Initialization cancelled by user.")
            return False
    
    # Copy template files
    copy_template_files(template_path, project_root)
    
    # Create symlinks for rules and commands
    create_symlinks_in_pages(project_root)
    
    print("\n✅ Project initialization completed successfully!")
    print("📁 Template directories copied:")
    for dir_name in TEMPLATE_DIRS_TO_COPY:
        print(f"   - {dir_name}/")
    print("\n🔗 Symbolic links created in pages/ for rules and commands")
    print("\n🎯 Next steps:")
    print("   1. Review the copied template files")
    print("   2. Run `uv run python scripts/development/generate_logseq_config.py` to update graph configuration")
    print("   3. Start using your new RooCode-powered project!")
    
    return True


def update_project(project_root: Path, template_path: Path):
    """
    Update an existing project with new template files safely.
    This is the --update mode implementation.
    """
    print("\n--- 🔄 Updating existing project with latest RooCode template ---")
    
    # Check if required template directories exist
    missing_dirs = []
    for dir_name in TEMPLATE_DIRS_TO_COPY:
        source_dir = template_path / dir_name
        if not source_dir.is_dir():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"⚠️  Warning: The following template directories are missing: {', '.join(missing_dirs)}")
    
    # Update template files safely
    stats = update_template_files(template_path, project_root)
    
    # Create symlinks for rules and commands (update existing ones)
    create_symlinks_in_pages(project_root)
    
    # Print summary
    print("\n📊 Update Summary:")
    print(f"   ✅ Added files: {stats['added']}")
    print(f"   🔄 Updated files: {stats['updated']}")
    print(f"   ⏭️  Skipped files (user modified): {stats['skipped']}")
    if stats['errors'] > 0:
        print(f"   ❌ Errors: {stats['errors']}")
    
    if stats['skipped'] > 0:
        print("\n⚠️  Some files were skipped because they were modified by you.")
        print("   This is to preserve your changes. If you want to update these files,")
        print("   review the changes in the template and manually merge them.")
    
    print("\n✅ Project update completed successfully!")
    print("\n🎯 Next steps:")
    print("   1. Review the updated template files")
    print("   2. Run `uv run python scripts/development/generate_logseq_config.py` to update graph configuration if needed")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap script for RooCode project template initialization, migration, and updates.",
        epilog="Examples:\n"
               "  python bootstrap.py --init          # Initialize new project\n"
               "  python bootstrap.py --migrate       # Migrate existing project\n"
               "  python bootstrap.py --update        # Update existing project with latest template\n"
               "  python bootstrap.py --init --repo https://github.com/user/custom-template.git",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--init", action='store_true', help="Initialize a new project with RooCode template files")
    parser.add_argument("--migrate", action='store_true', help="Migrate existing documentation to pages/ directory")
    parser.add_argument("--update", action='store_true', help="Update existing project with latest template files (safe update)")
    parser.add_argument("--repo", type=str, default="https://github.com/ozand/roo-project-template.git", 
                       help="URL of the RooCode template repository (default: official template)")
    
    args = parser.parse_args()
    
    # Validate that exactly one mode is specified
    mode_count = sum([args.init, args.migrate, args.update])
    if mode_count == 0:
        parser.error("Please specify one of --init, --migrate, or --update mode")
    elif mode_count > 1:
        parser.error("Please specify only one mode: --init, --migrate, or --update")
    
    project_root = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Cloning template from {args.repo}...")
        if not run_command(["git", "clone", args.repo, "."], cwd=temp_dir):
            print("❌ Failed to clone template repository. Aborting execution.")
            return

        template_path = Path(temp_dir)
        
        if args.init:
            # Initialize new project
            if not init_project(project_root, template_path):
                return
        elif args.migrate:
            # Migrate existing project
            copy_template_files(template_path, project_root)
            migrate_existing_docs(project_root)
            create_symlinks_in_pages(project_root)
            
            print("\n🎉 Migration process completed!")
            print("➡️  It is recommended to run `uv run python scripts/development/generate_logseq_config.py` to update graph configuration.")
        elif args.update:
            # Update existing project
            if not update_project(project_root, template_path):
                return


if __name__ == "__main__":
    main()