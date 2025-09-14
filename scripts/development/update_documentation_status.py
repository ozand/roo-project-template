#!/usr/bin/env python3
"""
Automated Documentation Status Update Script

This script implements the documentation maintenance protocol triggered by Git commits 
or direct task completion commands. It automatically updates documentation status
across sprint plans, backlogs, and requirements based on task completion.

Features:
- Extract task IDs from commit messages using regex patterns
- Update task status in sprint-plan.md from In Progress/TODO to Done
- Automatically update story status in backlog.md when all related tasks are done
- Update requirement status in requirements.md based on story completion
- Run consistency checks to ensure documentation integrity
- Support for both commit message and direct task ID input
- Comprehensive error handling and logging

Usage:
    python scripts/development/update_documentation_status.py --commit-message "Closes TASK-S1-1"
    python scripts/development/update_documentation_status.py --task-id TASK-S1-1
    python scripts/development/update_documentation_status.py --check-only

Integration:
    This script is designed to be integrated with Git hooks and CI/CD pipelines
    to automatically maintain documentation consistency.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def log_info(message: str) -> None:
    """Log informational messages to stdout."""
    print(f"ℹ️  {message}")


def log_error(message: str) -> None:
    """Log error messages to stderr."""
    print(f"❌ {message}", file=sys.stderr)


def log_warning(message: str) -> None:
    """Log warning messages to stderr."""
    print(f"⚠️  {message}", file=sys.stderr)


class DocumentationUpdater:
    """Handles automated documentation status updates and consistency checks."""
    
    def __init__(self, pages_dir: str = "pages"):
        self.pages_dir = Path(pages_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def extract_task_id_from_commit(self, commit_message: str) -> Optional[str]:
        """Extract task ID from commit message using regex pattern."""
        pattern = r'Closes\s+(TASK-[A-Z0-9-]+)'
        match = re.search(pattern, commit_message, re.IGNORECASE)
        if match:
            task_id = match.group(1)
            log_info(f"Extracted task ID '{task_id}' from commit message")
            return task_id
        log_warning(f"No task ID found in commit message: {commit_message}")
        return None
    
    def update_sprint_plan(self, task_id: str) -> bool:
        """Update task status in sprint plan from In Progress/TODO to Done."""
        sprint_file = self.pages_dir / "sprint-plan.md"
        if not sprint_file.exists():
            log_error(f"Sprint plan file not found: {sprint_file}")
            return False
            
        try:
            content = sprint_file.read_text(encoding='utf-8')
            
            # Find and update task status - handle both In Progress and TODO statuses
            pattern = rf'(\|\s*{re.escape(task_id)}\s*\|.*?\|\s*)(In Progress|TODO)(\s*\|)'
            replacement = r'\1Done\3'
            
            if not re.search(pattern, content):
                log_warning(f"Task {task_id} not found or already marked as Done")
                return False
                
            updated_content = re.sub(pattern, replacement, content)
            sprint_file.write_text(updated_content, encoding='utf-8')
            log_info(f"Updated task {task_id} status to Done in sprint plan")
            return True
            
        except Exception as e:
            log_error(f"Failed to update sprint plan: {e}")
            return False
    
    def update_backlog_from_task(self, task_id: str) -> bool:
        """Update story status in backlog when all related tasks are completed."""
        try:
            # Extract story ID from the task (TASK-S1-1 -> STORY-S1-1)
            story_id = task_id.replace("TASK-", "STORY-", 1)
            log_info(f"Checking story {story_id} completion status")
            
            # Read sprint plan to check if all tasks for this story are done
            sprint_file = self.pages_dir / "sprint-plan.md"
            if not sprint_file.exists():
                log_error("Sprint plan file not found")
                return False
                
            sprint_content = sprint_file.read_text(encoding='utf-8')
            
            # Find all tasks for this story
            story_tasks = []
            for line in sprint_content.split('\n'):
                if story_id.replace("STORY-", "TASK-") in line:
                    story_tasks.append(line)
            
            if not story_tasks:
                log_warning(f"No tasks found for story {story_id}")
                return False
            
            # Check if all tasks are done
            all_done = True
            for task_line in story_tasks:
                if "| Done |" not in task_line and "| In Progress |" in task_line or "| TODO |" in task_line:
                    all_done = False
                    break
            
            if not all_done:
                log_info(f"Story {story_id} has incomplete tasks, skipping backlog update")
                return False
            
            # Update backlog if all tasks are done
            backlog_file = self.pages_dir / "backlog.md"
            if not backlog_file.exists():
                log_error("Backlog file not found")
                return False
                
            backlog_content = backlog_file.read_text(encoding='utf-8')
            
            # Update story status to Done
            pattern = rf'(\|\s*{re.escape(story_id)}\s*\|.*?\|\s*)(In Progress|TODO)(\s*\|)'
            replacement = r'\1Done\3'
            
            if not re.search(pattern, backlog_content):
                log_warning(f"Story {story_id} not found or already marked as Done in backlog")
                return False
                
            updated_content = re.sub(pattern, replacement, backlog_content)
            backlog_file.write_text(updated_content, encoding='utf-8')
            log_info(f"Updated story {story_id} status to Done in backlog")
            return True
            
        except Exception as e:
            log_error(f"Failed to update backlog: {e}")
            return False
    
    def update_requirements_from_story(self, story_id: str) -> bool:
        """Update requirement status based on story completion."""
        try:
            # Extract requirement ID from story (STORY-S1-1 -> REQ-S1-1)
            req_id = story_id.replace("STORY-", "REQ-", 1)
            log_info(f"Checking requirement {req_id} completion status")
            
            # Read backlog to check if all stories for this requirement are done
            backlog_file = self.pages_dir / "backlog.md"
            if not backlog_file.exists():
                log_error("Backlog file not found")
                return False
                
            backlog_content = backlog_file.read_text(encoding='utf-8')
            
            # Find all stories for this requirement
            req_stories = []
            for line in backlog_content.split('\n'):
                if req_id.replace("REQ-", "STORY-") in line:
                    req_stories.append(line)
            
            if not req_stories:
                log_warning(f"No stories found for requirement {req_id}")
                return False
            
            # Check if all stories are done
            all_done = True
            done_count = 0
            total_count = 0
            
            for story_line in req_stories:
                total_count += 1
                if "| Done |" in story_line:
                    done_count += 1
                elif "| In Progress |" in story_line or "| TODO |" in story_line:
                    all_done = False
            
            # Determine new status
            if all_done and done_count > 0:
                new_status = "IMPLEMENTED"
            elif done_count > 0:
                new_status = "PARTIAL"
            else:
                log_info(f"No completed stories for requirement {req_id}, skipping update")
                return False
            
            # Update requirements file
            requirements_file = self.pages_dir / "requirements.md"
            if not requirements_file.exists():
                log_error("Requirements file not found")
                return False
                
            requirements_content = requirements_file.read_text(encoding='utf-8')
            
            # Update requirement status
            pattern = rf'(\|\s*{re.escape(req_id)}\s*\|.*?\|\s*)(PLANNED|PARTIAL|IMPLEMENTED)(\s*\|)'
            replacement = rf'\1{new_status}\3'
            
            if not re.search(pattern, requirements_content):
                log_warning(f"Requirement {req_id} not found or already has status {new_status}")
                return False
                
            updated_content = re.sub(pattern, replacement, requirements_content)
            requirements_file.write_text(updated_content, encoding='utf-8')
            log_info(f"Updated requirement {req_id} status to {new_status}")
            return True
            
        except Exception as e:
            log_error(f"Failed to update requirements: {e}")
            return False
    
    def check_backlog_requirements_integrity(self) -> bool:
        """Check that every Req. ID in backlog.md exists in requirements.md."""
        try:
            backlog_file = self.pages_dir / "backlog.md"
            requirements_file = self.pages_dir / "requirements.md"
            
            if not backlog_file.exists() or not requirements_file.exists():
                log_warning("Required files for integrity check not found")
                return True  # Don't fail on missing files
            
            backlog_content = backlog_file.read_text(encoding='utf-8')
            requirements_content = requirements_file.read_text(encoding='utf-8')
            
            # Extract requirement IDs from both files
            backlog_reqs = set(re.findall(r'REQ-[A-Z]+-\d+', backlog_content))
            requirements_reqs = set(re.findall(r'REQ-[A-Z]+-\d+', requirements_content))
            
            missing_reqs = backlog_reqs - requirements_reqs
            if missing_reqs:
                self.errors.append(f"Missing requirements in requirements.md: {missing_reqs}")
                return False
            
            log_info("Backlog-requirements integrity check passed")
            return True
            
        except Exception as e:
            log_error(f"Backlog-requirements integrity check failed: {e}")
            return False
    
    def check_roadmap_backlog_integrity(self) -> bool:
        """Check that every Epic ID in roadmap.md exists in backlog.md."""
        try:
            roadmap_file = self.pages_dir / "roadmap.md"
            backlog_file = self.pages_dir / "backlog.md"
            
            if not roadmap_file.exists() or not backlog_file.exists():
                log_warning("Required files for roadmap-backlog integrity check not found")
                return True  # Don't fail on missing files
            
            roadmap_content = roadmap_file.read_text(encoding='utf-8')
            backlog_content = backlog_file.read_text(encoding='utf-8')
            
            # Extract epic IDs from both files
            roadmap_epics = set(re.findall(r'EPIC-[A-Z]+', roadmap_content))
            backlog_epics = set(re.findall(r'EPIC-[A-Z]+', backlog_content))
            
            missing_epics = roadmap_epics - backlog_epics
            if missing_epics:
                self.errors.append(f"Missing epics in backlog.md: {missing_epics}")
                return False
            
            log_info("Roadmap-backlog integrity check passed")
            return True
            
        except Exception as e:
            log_error(f"Roadmap-backlog integrity check failed: {e}")
            return False
    
    def check_sprint_backlog_integrity(self) -> bool:
        """Check that every Story ID in sprint-plan.md exists in backlog.md."""
        try:
            sprint_file = self.pages_dir / "sprint-plan.md"
            backlog_file = self.pages_dir / "backlog.md"
            
            if not sprint_file.exists() or not backlog_file.exists():
                log_warning("Required files for sprint-backlog integrity check not found")
                return True  # Don't fail on missing files
            
            sprint_content = sprint_file.read_text(encoding='utf-8')
            backlog_content = backlog_file.read_text(encoding='utf-8')
            
            # Extract story IDs from both files
            sprint_stories = set(re.findall(r'STORY-[A-Z]+-\d+', sprint_content))
            backlog_stories = set(re.findall(r'STORY-[A-Z]+-\d+', backlog_content))
            
            missing_stories = sprint_stories - backlog_stories
            if missing_stories:
                self.errors.append(f"Missing stories in backlog.md: {missing_stories}")
                return False
            
            log_info("Sprint-backlog integrity check passed")
            return True
            
        except Exception as e:
            log_error(f"Sprint-backlog integrity check failed: {e}")
            return False
    
    def check_status_consistency(self) -> None:
        """Check status consistency between requirements and stories."""
        try:
            requirements_file = self.pages_dir / "requirements.md"
            backlog_file = self.pages_dir / "backlog.md"
            
            if not requirements_file.exists() or not backlog_file.exists():
                log_warning("Required files for status consistency check not found")
                return
            
            requirements_content = requirements_file.read_text(encoding='utf-8')
            backlog_content = backlog_file.read_text(encoding='utf-8')
            
            # Find implemented requirements
            implemented_reqs = []
            for line in requirements_content.split('\n'):
                if "| IMPLEMENTED |" in line:
                    req_match = re.search(r'REQ-[A-Z]+-\d+', line)
                    if req_match:
                        implemented_reqs.append(req_match.group(0))
            
            # Check if all stories for implemented requirements are done
            for req_id in implemented_reqs:
                req_stories = []
                for line in backlog_content.split('\n'):
                    if req_id.replace("REQ-", "STORY-") in line:
                        req_stories.append(line)
                
                incomplete_stories = []
                for story_line in req_stories:
                    if "| Done |" not in story_line and ("| In Progress |" in story_line or "| TODO |" in story_line):
                        story_match = re.search(r'STORY-[A-Z]+-\d+', story_line)
                        if story_match:
                            incomplete_stories.append(story_match.group(0))
                
                if incomplete_stories:
                    self.warnings.append(f"Requirement {req_id} is IMPLEMENTED but has incomplete stories: {incomplete_stories}")
            
            log_info("Status consistency check completed")
            
        except Exception as e:
            log_error(f"Status consistency check failed: {e}")
    
    def run_consistency_checks(self) -> bool:
        """Run all consistency checks and return overall result."""
        log_info("Running consistency checks...")
        checks_passed = True
        
        try:
            # Run all integrity checks
            checks_passed &= self.check_backlog_requirements_integrity()
            checks_passed &= self.check_roadmap_backlog_integrity()
            checks_passed &= self.check_sprint_backlog_integrity()
            
            # Status consistency only warns, doesn't fail
            self.check_status_consistency()
            
            # Report results
            if self.errors:
                log_error(f"Consistency checks failed with {len(self.errors)} errors")
                for error in self.errors:
                    log_error(f"  - {error}")
                checks_passed = False
            
            if self.warnings:
                log_warning(f"Consistency checks found {len(self.warnings)} warnings")
                for warning in self.warnings:
                    log_warning(f"  - {warning}")
            
            if checks_passed and not self.errors and not self.warnings:
                log_info("All consistency checks passed")
            
        except Exception as e:
            log_error(f"Consistency check failed with exception: {e}")
            checks_passed = False
            
        return checks_passed


def main():
    """Main entry point with argument parsing and execution logic."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update documentation status across sprint plans, backlogs, and requirements",
        epilog="Examples:\n"
               "  %(prog)s --commit-message \"Closes TASK-S1-1\"\n"
               "  %(prog)s --task-id TASK-S1-1\n"
               "  %(prog)s --check-only",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--commit-message", 
        help="Git commit message containing task closure information"
    )
    parser.add_argument(
        "--task-id", 
        help="Direct task ID to update (e.g., TASK-S1-1)"
    )
    parser.add_argument(
        "--check-only", 
        action="store_true", 
        help="Only run consistency checks without making updates"
    )
    parser.add_argument(
        "--pages-dir", 
        default="pages", 
        help="Directory containing documentation files (default: pages)"
    )
    
    args = parser.parse_args()
    
    # Initialize updater
    updater = DocumentationUpdater(pages_dir=args.pages_dir)
    
    # Handle check-only mode
    if args.check_only:
        log_info("Running in check-only mode")
        success = updater.run_consistency_checks()
        sys.exit(0 if success else 1)
    
    # Determine task ID from commit message or direct input
    task_id = None
    if args.commit_message:
        task_id = updater.extract_task_id_from_commit(args.commit_message)
        if not task_id:
            log_error("No task ID found in commit message")
            sys.exit(1)
    elif args.task_id:
        task_id = args.task_id
    else:
        log_error("Either --commit-message or --task-id must be provided")
        sys.exit(1)
    
    log_info(f"Processing task: {task_id}")
    
    # Execute update protocol
    success = True
    
    # Step 1: Update sprint plan
    sprint_success = updater.update_sprint_plan(task_id)
    if not sprint_success:
        success = False
    
    # Step 2: Update backlog from task
    if success:
        backlog_success = updater.update_backlog_from_task(task_id)
        if not backlog_success:
            log_warning("Backlog update failed, continuing with consistency checks")
    
    # Step 3: Update requirements from story
    if success:
        # Extract story ID from task and update requirements
        story_id = task_id.replace("TASK-", "STORY-", 1)
        req_success = updater.update_requirements_from_story(story_id)
        if not req_success:
            log_warning("Requirements update failed, continuing with consistency checks")
    
    # Run consistency checks
    consistency_success = updater.run_consistency_checks()
    if not consistency_success:
        success = False
    
    # Final result
    if success:
        log_info("Documentation update completed successfully")
        sys.exit(0)
    else:
        log_error("Documentation update completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()