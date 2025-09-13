#!/usr/bin/env python3
"""
Bootstrap script for RooCode project template initialization and migration.
Supports both --init (new project setup) and --migrate (existing project migration) modes.
"""

import subprocess
import sys
import shutil
import tempfile
import argparse
import os
from pathlib import Path

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


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap script for RooCode project template initialization and migration.",
        epilog="Examples:\n"
               "  python bootstrap.py --init          # Initialize new project\n"
               "  python bootstrap.py --migrate       # Migrate existing project\n"
               "  python bootstrap.py --init --repo https://github.com/user/custom-template.git",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--init", action='store_true', help="Initialize a new project with RooCode template files")
    parser.add_argument("--migrate", action='store_true', help="Migrate existing documentation to pages/ directory")
    parser.add_argument("--repo", type=str, default="https://github.com/ozand/roo-project-template.git", 
                       help="URL of the RooCode template repository (default: official template)")
    
    args = parser.parse_args()
    
    # Validate that at least one mode is specified
    if not args.init and not args.migrate:
        parser.error("Please specify either --init or --migrate mode")
    
    # Both modes cannot be used together
    if args.init and args.migrate:
        parser.error("--init and --migrate modes cannot be used together")
    
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


if __name__ == "__main__":
    main()