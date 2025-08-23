#!/usr/bin/env python3
"""
Knowledge Base Validation Script

This script validates the knowledge base structure according to the rules defined in
the project's knowledge base standard. It operates on a "whitelist" of directories,
only scanning folders that are explicitly part of the knowledge base.

Usage:
    python scripts/development/validate_kb.py
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List
from datetime import datetime

class KBValidator:
    """Knowledge Base Validator using a whitelist approach."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.errors = []
        self.warnings = []

        # --- НОВОЕ: "Белый список" директорий для валидации. ---
        # Скрипт будет работать ТОЛЬКО с файлами внутри этих папок.
        self.knowledge_base_dirs = {
            "pages",
            "journals",
            "docs", # Добавляем 'docs' для поддержки вашего текущего расположения
            ".roo/rules" # И правила, которые являются частью стандарта
        }

    def _find_markdown_files(self) -> List[Path]:
        """
        Находит все .md файлы в проекте, сканируя только директории
        из "белого списка" (self.knowledge_base_dirs).
        """
        markdown_files = []
        print("\nScanning whitelisted directories:")
        for kb_dir_name in self.knowledge_base_dirs:
            kb_dir_path = self.base_path / kb_dir_name
            if kb_dir_path.is_dir():
                print(f"  - Scanning '{kb_dir_name}'...")
                # Рекурсивно ищем все .md файлы внутри разрешенной директории
                files_in_dir = list(kb_dir_path.rglob("*.md"))
                markdown_files.extend(files_in_dir)
            else:
                self.warnings.append(f"Knowledge base directory '{kb_dir_name}' not found.")
        
        return markdown_files

    def validate(self):
        """Run all validation checks on the discovered files."""
        print(f"Project root: {self.base_path}")
        all_md_files = self._find_markdown_files()
        print(f"\nFound {len(all_md_files)} markdown files for validation.")

        if not all_md_files:
            self.warnings.append("No markdown files found in the knowledge base directories.")
            return

        for md_file in all_md_files:
            # Здесь ваша детальная логика валидации каждого файла:
            # self.validate_properties(md_file)
            # self.validate_links(md_file)
            pass

    # ... (здесь находятся остальные ваши функции валидации) ...

    def fix_all_issues(self):
        """(Placeholder) Fix all found validation issues."""
        print("Fixing issues...")
        # Логика исправления будет здесь
        pass
    
    def generate_report(self, output_file: Path):
        """Generate a validation report."""
        report_content = f"# Knowledge Base Validation Report - {datetime.now().isoformat()}\n\n"
        # ... (логика генерации отчета) ...
        print(f"Report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Knowledge Base Validator')
    parser.add_argument(
        '--project-root', 
        type=Path, 
        default=Path.cwd(),
        help='The root directory of the project to validate.'
    )
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--report', type=str, help='Output report file')
    parser.add_argument('--fix', action='store_true', help='Attempt to automatically fix issues')

    args = parser.parse_args()

    validator = KBValidator(args.project_root)

    if args.fix:
        print("Attempting to fix validation issues...")
        validator.fix_all_issues()
        print("Fixing process complete!")
        return

    print("Running validation...")
    validator.validate()

    if args.report:
        report_file = Path(args.report)
        validator.generate_report(report_file)

    if validator.errors or validator.warnings:
        print(f"\nFound {len(validator.errors)} errors and {len(validator.warnings)} warnings.")
        # ... (логика вывода ошибок) ...
        sys.exit(1)
    else:
        print("\n✅ All validation checks passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()