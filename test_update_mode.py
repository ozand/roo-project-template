#!/usr/bin/env python3
"""
Test script for verifying the --update mode functionality in bootstrap.py
"""

import os
import sys
import tempfile
import shutil
import subprocess
import hashlib
from pathlib import Path


def create_test_project_structure(project_dir: Path):
    """Create a test project structure similar to a RooCode project."""
    # Create directories
    dirs = [".roo/rules", ".roo/commands", "scripts/development", "pages", "docs", "journals"]
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create some sample files
    sample_files = {
        ".roo/rules/01-quality_guideline.md": "# Quality Guideline\n\nThis is a sample rule file.",
        ".roo/commands/init.md": "# Init Command\n\nThis is a sample command file.",
        "scripts/development/utils.py": "# Utility functions\n\ndef hello():\n    return 'Hello World'",
        "pages/STORY-TEST-1.md": "# Test Story\n\ntype:: [[story]]\nstatus:: [[TODO]]",
        "docs/guide.md": "# Documentation Guide\n\nThis is a sample documentation file.",
        "README.md": "# Test Project\n\nThis is a test project for bootstrap update mode."
    }
    
    for file_path, content in sample_files.items():
        full_path = project_dir / file_path
        full_path.write_text(content)


def modify_file_for_testing(file_path: Path):
    """Modify a file to simulate user changes."""
    original_content = file_path.read_text()
    modified_content = original_content + "\n\n# User Modification\n\nThis was added by the user."
    file_path.write_text(modified_content)


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def test_update_mode():
    """Test the --update mode functionality."""
    print("🧪 Testing --update mode functionality...")
    
    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "test_project"
        project_dir.mkdir()
        
        # Create initial project structure
        print("📁 Creating initial project structure...")
        create_test_project_structure(project_dir)
        
        # Modify some files to simulate user changes
        print("✍️  Simulating user modifications...")
        user_modified_file = project_dir / "README.md"
        original_hash = calculate_file_hash(user_modified_file)
        modify_file_for_testing(user_modified_file)
        modified_hash = calculate_file_hash(user_modified_file)
        
        print(f"   Original README.md hash: {original_hash[:16]}...")
        print(f"   Modified README.md hash: {modified_hash[:16]}...")
        
        # Try to run the update mode
        print("🚀 Running bootstrap.py --update...")
        try:
            # Run the bootstrap script with --update mode
            result = subprocess.run([
                sys.executable, 
                str(Path(__file__).parent / "bootstrap.py"), 
                "--update"
            ], cwd=str(project_dir), capture_output=True, text=True, timeout=60)
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
            
            if result.returncode == 0:
                print("✅ Update mode executed successfully!")
                
                # Check if files were handled correctly
                readme_content = (project_dir / "README.md").read_text()
                if "User Modification" in readme_content:
                    print("✅ User modifications were preserved in README.md")
                else:
                    print("❌ User modifications were lost in README.md")
                
                # Check if template hash file was created
                hash_file = project_dir / ".roo" / ".template_hashes.json"
                if hash_file.exists():
                    print("✅ Template hash file was created")
                else:
                    print("❌ Template hash file was not created")
                    
                return True
            else:
                print("❌ Update mode failed!")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Update mode timed out!")
            return False
        except Exception as e:
            print(f"❌ Error running update mode: {e}")
            return False


def test_help_text():
    """Test that help text includes --update option."""
    print("\n📖 Testing help text...")
    try:
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent / "bootstrap.py"), 
            "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if "--update" in result.stdout:
            print("✅ Help text includes --update option")
            return True
        else:
            print("❌ Help text does not include --update option")
            print(f"STDOUT:\n{result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing help text: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting bootstrap.py --update mode tests...\n")
    
    # Test help text
    help_success = test_help_text()
    
    # Test update mode functionality
    update_success = test_update_mode()
    
    print("\n📋 Test Summary:")
    print(f"   Help text test: {'✅ PASSED' if help_success else '❌ FAILED'}")
    print(f"   Update mode test: {'✅ PASSED' if update_success else '❌ FAILED'}")
    
    if help_success and update_success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)