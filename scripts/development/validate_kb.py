#!/usr/bin/env python3
"""
Скрипт для Валидации Базы Знаний (Knowledge Base)

Этот скрипт проверяет целостность базы знаний Logseq согласно правилам,
определенным в стандарте проекта. Он реализует следующие проверки:
  1.  **Целостность ссылок:** Убеждается, что все ссылки `[[...]]` в файлах
      указывают на существующие страницы (.md файлы). При этом ссылки в
      блоках кода (fenced ```...``` и inline `...`) игнорируются для
      предотвращения ложных срабатываний.
  2.  **Правильное форматирование ссылок:** Проверяет, что все ссылки на
      внешние файлы (код, тесты) следуют формату с алиасом `[[path|`file`]]`.
      Ссылки в блоках кода также игнорируются.
  3.  **Структура файлов:** Проверяет, что все документы созданы в правильных
      директориях и следуют соглашениям по именованию.
  4.  **Схема свойств:** Проверяет, что все User Stories и Requirements имеют
      обязательные свойства.
  5.  **Правильность статусов:** Проверяет, что значения свойства status
      соответствуют разрешенному списку.
  6.  **Целостность заголовков в README:** Проверяет, что все README.md файлы
      имеют свойство title::.
  7.  **Обработка временных артефактов:** Проверяет, что файлы с "сырыми"
      выводами команд не сохраняются в pages/.

Для игнорирования ссылок в блоках кода используется вспомогательная функция
`_remove_code_blocks`, которая удаляет как fenced code blocks (```...```), так
и inline code blocks (`...`) из содержимого markdown перед извлечением ссылок.
Это позволяет избежать ложных срабатываний при проверке ссылок в примерах кода
в файлах правил.

Использование:
    python scripts/development/validate_kb.py
"""

import re
import sys
import os
import logging
from pathlib import Path
from typing import List, Set
from datetime import datetime
import argparse

# --- Конфигурация ---

# Директории, которые являются частью базы знаний и подлежат сканированию.
KNOWLEDGE_BASE_DIRS = {"pages", "journals"}

# Разрешенные файлы в корне проекта
ALLOWED_ROOT_FILES = {"README.md", "CONTRIBUTING.md"}

# Ссылки, которые нужно игнорировать при проверке, так как они не являются файлами.
# (например, статусы, теги, свойства).
# Расширенный список для фильтрации "dummy" концептуальных ссылок.
IGNORED_LINKS = {
    # Статусы задач и требований
    "TODO", "DOING", "DONE",
    "PLANNED", "IMPLEMENTED", "PARTIAL",
    "DRAFT", "APPROVED", "COMPLETED",
    
    # Приоритеты
    "high", "medium", "low",
    
    # Типы документов
    "story", "requirement", "implementation-plan", "learning",
    
    # Концептуальные категории из схем свойств
    "epic", "positive", "negative", "technical", "process", "communication",
    
    # Роли пользователей (с префиксом @)
    "@developer", "@architect", "@team", "@username",
    
    # Фаза проекта (шаблоны для разных фаз)
    "Phase-1", "Phase-2", "Phase-3", "Phase-4", "Phase-5", "Phase-6", "Phase-7", "Phase-8", "Phase-9", "Phase-10",
    "Phase-X", "Phase-Y", "Phase-Z",
    
    # Дополнительные концептуальные ссылки, которые могут встречаться
    "EPIC-NAME", "EPIC-UI", "EPIC-INFRA", "REQ-ID-1", "REQ-ID-2",  # Примеры из шаблонов
    "STORY-API-5", "STORY-UI-12",  # Примеры из шаблонов
    "LEARNING-ID",  # Пример из шаблонов
    
    # Общие концепты, которые могут использоваться в документации
    "product.vision", "requirements", "backlog", "roadmap", "api", "caching-strategy", "DEPLOYMENT_PLAN",
    "rules.quality-guideline", "rules.scripts-structure", "rules.e2e-tests-guideline", "rules.filename-referencing-rules",

    # Новые концептуальные ссылки
    "concept", "documentation", "meta-documentation",
    "queries", "centralized-query-library", "active"
}

class KBValidator:
    """Валидатор Базы Знаний, реализующий все проверки."""

    def __init__(self, base_path: Path):
        self.base_path = base_path.resolve()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.terminal_errors: List[str] = []
        self.external_errors: List[str] = []
        self.filtered_links: List[str] = []  # Новый список для отфильтрованных ссылок
        self.valid_agent_roles = self._extract_valid_agent_roles()  # Извлекаем допустимые роли агентов
        # Регулярное выражение для поиска всех ссылок [[...]]
        self.link_pattern = re.compile(r"\[\[([^\]]+)\]\]")
        # Регулярные выражения для проверки имен файлов
        self.story_pattern = re.compile(r"^STORY-[A-Z]+-\d+\.md$")
        self.req_pattern = re.compile(r"^REQ-[A-Z]+-\d+\.md$")
        self.rule_pattern = re.compile(r"^\.roo/rules/[^/]+\.md$")
        # Регулярное выражение для поиска ссылок с алиасами
        self.alias_link_pattern = re.compile(r"\[\[([^\]|]+)\|`([^`]+)`\]\]")
        # Загружаем паттерны из .gitignore
        self.gitignore_patterns = self._load_gitignore()
        # Настраиваем логирование
        self._setup_logging()

    def _setup_logging(self):
        """Настраивает логирование в файл."""
        log_dir = self.base_path / "log"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"validate_kb_{timestamp}.log"
        
        # Create separate loggers for file and console
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # File handler - logs everything
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Console handler - only logs warnings and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only show warnings and errors in terminal
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Validation started. Log file: {log_file}")

    def _is_knowledge_base_file(self, file_path: Path) -> bool:
        """Проверяет, находится ли файл в директориях базы знаний."""
        try:
            relative_path = file_path.relative_to(self.base_path).as_posix()
            return (
                relative_path.startswith("pages/") or 
                relative_path.startswith("journals/") or 
                relative_path.startswith(".roo/rules/")
            )
        except ValueError:
            return False

    def _add_error(self, error_msg: str, file_path: Path = None):
        """Добавляет ошибку с учетом категоризации."""
        if file_path and self._is_knowledge_base_file(file_path):
            self.terminal_errors.append(error_msg)
            self.logger.error(error_msg)
        else:
            self.external_errors.append(error_msg)
            self.logger.info(error_msg)  # Changed to info level for external files
        self.errors.append(error_msg)

    def _add_warning(self, warning_msg: str):
        """Добавляет предупреждение."""
        self.warnings.append(warning_msg)
        self.logger.warning(warning_msg)

    def _load_gitignore(self) -> List[str]:
        """Загружает и парсит паттерны из .gitignore."""
        gitignore_path = self.base_path / ".gitignore"
        patterns = []
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # Пропускаем пустые строки и комментарии
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except Exception as e:
                self._add_warning(f"Не удалось прочитать .gitignore: {e}")
        
        return patterns

    def _is_ignored(self, file_path: Path) -> bool:
        """Проверяет, игнорируется ли файл по паттернам из .gitignore."""
        try:
            relative_path = file_path.relative_to(self.base_path).as_posix()
            
            for pattern in self.gitignore_patterns:
                # Преобразуем паттерн в регулярное выражение
                # Это упрощенная реализация, не охватывает все случаи gitignore
                regex_pattern = pattern.replace(".", "\\.").replace("*", ".*").replace("?", ".?")
                
                # Если паттерн заканчивается на /, это директория
                if pattern.endswith("/"):
                    regex_pattern = regex_pattern.rstrip("/") + "/.*"
                
                # Компилируем регулярное выражение
                try:
                    if re.match(regex_pattern, relative_path) or re.match(regex_pattern, relative_path + "/"):
                        return True
                except re.error:
                    # Игнорируем некорректные регулярные выражения
                    continue
        except ValueError:
            # Если не удалось получить относительный путь, считаем файл не игнорируемым
            pass
        
        return False

    def _remove_code_blocks(self, content: str) -> str:
        """Удаляет блоки кода из содержимого markdown перед проверкой ссылок."""
        # Удаляем fenced code blocks (```...```)
        fenced_pattern = re.compile(r"```.*?```", re.DOTALL)
        content_without_fenced = re.sub(fenced_pattern, "", content)
        
        # Удаляем inline code blocks (`...`)
        inline_pattern = re.compile(r"`[^`]*`")
        content_without_code = re.sub(inline_pattern, "", content_without_fenced)
        
        return content_without_code

    def _extract_valid_agent_roles(self) -> List[str]:
        """Извлекает допустимые роли агентов из документа возможностей агентов."""
        valid_roles = []
        agent_capabilities_path = self.base_path / ".roo/rules/05-agent_capabilities.md"
        
        if not agent_capabilities_path.exists():
            self._add_warning(f"Файл возможностей агентов не найден: {agent_capabilities_path}")
            return valid_roles
        
        try:
            content = agent_capabilities_path.read_text(encoding="utf-8")
            # Ищем заголовки агентов в формате #### Иконка ИмяАгента
            agent_header_pattern = re.compile(r"^####\s+[^\s]+\s+(.+)$", re.MULTILINE)
            matches = agent_header_pattern.findall(content)
            
            for match in matches:
                # Очищаем имя агента от лишних символов
                role_name = match.strip()
                valid_roles.append(role_name)
                
        except Exception as e:
            self._add_warning(f"Не удалось извлечь роли агентов из {agent_capabilities_path}: {e}")
        
        return valid_roles

    def _find_markdown_files(self) -> List[Path]:
        """Находит все .md файлы, рекурсивно сканируя директории из KNOWLEDGE_BASE_DIRS."""
        markdown_files = []
        print("Сканирование директорий базы знаний:")
        for kb_dir_name in KNOWLEDGE_BASE_DIRS:
            kb_dir_path = self.base_path / kb_dir_name
            if kb_dir_path.is_dir():
                print(f"  - Сканирую '{kb_dir_name}'...")
                files_in_dir = list(kb_dir_path.rglob("*.md"))
                # Фильтруем файлы, игнорируемые по .gitignore
                filtered_files = [f for f in files_in_dir if not self._is_ignored(f)]
                markdown_files.extend(filtered_files)
            else:
                self._add_warning(f"Директория '{kb_dir_name}' не найдена и была пропущена.")
        
        # Также добавляем файлы из .roo/rules/
        rules_dir_path = self.base_path / ".roo/rules"
        if rules_dir_path.is_dir():
            print("  - Сканирую '.roo/rules'...")
            rules_files = list(rules_dir_path.rglob("*.md"))
            # Фильтруем файлы, игнорируемые по .gitignore
            filtered_rules_files = [f for f in rules_files if not self._is_ignored(f)]
            markdown_files.extend(filtered_rules_files)
        else:
            self._add_warning("Директория '.roo/rules' не найдена и была пропущена.")
        
        return markdown_files

    def _get_all_page_names(self, all_md_files: List[Path]) -> Set[str]:
        """Создает множество всех существующих имен страниц из имен файлов."""
        # Имя страницы - это имя файла без расширения .md
        return {file.stem for file in all_md_files}

    def validate_link_integrity(self, md_file: Path, all_pages: Set[str]):
        """Проверяет все ссылки в одном файле на существование."""
        try:
            content = md_file.read_text(encoding="utf-8")
            # Удаляем блоки кода перед извлечением ссылок
            content_without_code = self._remove_code_blocks(content)
            found_links = self.link_pattern.findall(content_without_code)

            for link in found_links:
                # Игнорируем ссылки с алиасами или пути к файлам
                if "|" in link or "/" in link or "\\" in link:
                    continue
                
                # Игнорируем специальные ссылки из списка IGNORED_LINKS и логируем их отдельно
                if link in IGNORED_LINKS:
                    relative_path = md_file.relative_to(self.base_path)
                    filter_msg = f"Filtered conceptual link in '{relative_path}': [[{link}]] (ignored as dummy link)"
                    self.filtered_links.append(filter_msg)
                    self.logger.info(filter_msg)  # Логируем как INFO для прозрачности
                    continue

                # Проверяем, существует ли страница для данной ссылки
                if link not in all_pages:
                    relative_path = md_file.relative_to(self.base_path)
                    self._add_error(f"Broken link in '{relative_path}': [[{link}]] points to a non-existent page.", md_file)

        except Exception as e:
            self._add_warning(f"Could not read or process file '{md_file}': {e}")


    def validate_correct_link_formatting(self, md_file: Path):
        """Проверяет, что ссылки на внешние файлы следуют правильному формату алиасов."""
        try:
            content = md_file.read_text(encoding="utf-8")
            # Удаляем блоки кода перед извлечением ссылок
            content_without_code = self._remove_code_blocks(content)
            # Находим все ссылки с алиасами
            found_alias_links = self.alias_link_pattern.findall(content_without_code)
            
            for path, filename in found_alias_links:
                # Проверяем, что имя файла в алиасе соответствует фактическому имени файла в пути
                # Например, [[path/to/file.py|`file.py`]] - здесь filename должно быть file.py
                actual_filename = Path(path).name
                if filename != actual_filename:
                    relative_path = md_file.relative_to(self.base_path)
                    self._add_error(f"Incorrect alias format in '{relative_path}': [[{path}|`{filename}`]] should be [[{path}|`{actual_filename}`]]", md_file)
                
                # Проверяем, что путь указывает на существующий файл (если это локальный путь)
                if not path.startswith("http") and not path.startswith("https"):
                    # Для локальных путей проверяем, что файл существует
                    path_obj = Path(path)
                    # Если путь относительный, проверяем относительно корня проекта
                    if not path_obj.is_absolute():
                        full_path = self.base_path / path_obj
                        if not full_path.exists():
                            relative_path = md_file.relative_to(self.base_path)
                            self._add_error(f"Link to non-existent file in '{relative_path}': [[{path}|`{filename}`]] points to a non-existent file.", md_file)

        except Exception as e:
            self._add_warning(f"Could not validate link formatting for '{md_file}': {e}")

    def validate_file_structure(self, md_file: Path):
        """Проверяет структуру файлов и соглашения по именованию."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            
            # Проверка User Stories
            if relative_path.startswith("pages/") and relative_path.endswith(".md"):
                filename = Path(relative_path).name
                if filename.startswith("STORY-"):
                    if not self.story_pattern.match(filename):
                        self._add_error(f"Неправильное имя файла User Story: '{relative_path}'. Должно быть в формате STORY-[CATEGORY]-[ID].md", md_file)
            
            # Проверка Requirements
            if relative_path.startswith("pages/") and relative_path.endswith(".md"):
                filename = Path(relative_path).name
                if filename.startswith("REQ-"):
                    if not self.req_pattern.match(filename):
                        self._add_error(f"Неправильное имя файла Requirement: '{relative_path}'. Должно быть в формате REQ-[CATEGORY]-[ID].md", md_file)
            
            # Проверка Rules (для файлов в .roo/rules/)
            if relative_path.startswith(".roo/rules/") and relative_path.endswith(".md"):
                # Проверка, что файлы правил находятся непосредственно в .roo/rules/, а не в поддиректориях
                path_parts = Path(relative_path).parts
                if len(path_parts) != 3:  # .roo/rules/filename.md
                    self._add_error(f"Файл правила должен находиться непосредственно в .roo/rules/: '{relative_path}'", md_file)

        except Exception as e:
            self._add_warning(f"Could not validate file structure for '{md_file}': {e}")

    def validate_properties_schema(self, md_file: Path):
        """Проверяет, что User Stories и Requirements имеют обязательные свойства."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            filename = Path(relative_path).name
            
            # Проверяем только файлы в директории pages
            if not relative_path.startswith("pages/"):
                return
            
            content = md_file.read_text(encoding="utf-8")
            
            # Проверка User Stories
            if filename.startswith("STORY-"):
                # Проверяем наличие всех обязательных свойств User Story
                required_properties = [
                    "type:: [[story]]",
                    "status::",
                    "priority::",
                    "assignee::",
                    "epic::",
                    "related-reqs::"
                ]
                
                missing_properties = []
                for prop in required_properties:
                    if prop not in content:
                        missing_properties.append(prop)
                
                if missing_properties:
                    self._add_error(f"User Story '{relative_path}' отсутствуют обязательные свойства: {', '.join(missing_properties)}", md_file)
            
            # Проверка Requirements
            elif filename.startswith("REQ-"):
                # Проверяем наличие всех обязательных свойств Requirement
                required_properties = [
                    "type:: [[requirement]]",
                    "status::"
                ]
                
                missing_properties = []
                for prop in required_properties:
                    if prop not in content:
                        missing_properties.append(prop)
                
                if missing_properties:
                    self._add_error(f"Requirement '{relative_path}' отсутствуют обязательные свойства: {', '.join(missing_properties)}", md_file)

        except Exception as e:
            self._add_warning(f"Could not validate properties schema for '{md_file}': {e}")

    def validate_status_correctness(self, md_file: Path):
        """Проверяет, что значения свойства status соответствуют разрешенному списку."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            filename = Path(relative_path).name
            
            # Проверяем только файлы в директории pages
            if not relative_path.startswith("pages/"):
                return
            
            content = md_file.read_text(encoding="utf-8")
            
            # Проверка User Stories
            if filename.startswith("STORY-"):
                # Найдем строку со статусом
                status_line = None
                for line in content.split('\n'):
                    if line.startswith("status::"):
                        status_line = line
                        break
                
                if status_line:
                    # Проверяем, что статус соответствует разрешенному списку
                    allowed_statuses = ["[[TODO]]", "[[DOING]]", "[[DONE]]"]
                    status_value = status_line.split("status::", 1)[1].strip()
                    if status_value not in allowed_statuses:
                        self._add_error(f"User Story '{relative_path}' имеет недопустимый статус: '{status_value}'. Допустимые значения: {', '.join(allowed_statuses)}", md_file)
            
            # Проверка Requirements
            elif filename.startswith("REQ-"):
                # Найдем строку со статусом
                status_line = None
                for line in content.split('\n'):
                    if line.startswith("status::"):
                        status_line = line
                        break
                
                if status_line:
                    # Проверяем, что статус соответствует разрешенному списку
                    allowed_statuses = ["[[PLANNED]]", "[[IMPLEMENTED]]", "[[PARTIAL]]"]
                    status_value = status_line.split("status::", 1)[1].strip()
                    if status_value not in allowed_statuses:
                        self._add_error(f"Requirement '{relative_path}' имеет недопустимый статус: '{status_value}'. Допустимые значения: {', '.join(allowed_statuses)}", md_file)

        except Exception as e:
            self._add_warning(f"Could not validate status correctness for '{md_file}': {e}")

    def validate_assignee_correctness(self, md_file: Path):
        """Проверяет, что значения свойства assignee соответствуют разрешенному списку."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            filename = Path(relative_path).name
            
            # Проверяем только файлы в директории pages
            if not relative_path.startswith("pages/"):
                return
            
            content = md_file.read_text(encoding="utf-8")
            
            # Проверка User Stories
            if filename.startswith("STORY-"):
                # Найдем строку с assignee
                assignee_line = None
                for line in content.split('\n'):
                    if line.startswith("assignee::"):
                        assignee_line = line
                        break
                
                if assignee_line:
                    # Проверяем, что assignee соответствует разрешенному списку
                    # Извлекаем значение из ссылки вида `[[@Agent Name]]`
                    assignee_match = re.search(r"`\[\[@(.+?)\]\]`", assignee_line)
                    if assignee_match:
                        assignee_value = assignee_match.group(1)
                        # Проверяем, что роль агента в списке допустимых
                        if assignee_value not in self.valid_agent_roles:
                            self._add_error(f"User Story '{relative_path}' имеет недопустимого assignee: '{assignee_value}'. Допустимые значения: {', '.join(self.valid_agent_roles)}", md_file)
                    else:
                        # Если не удалось извлечь значение assignee
                        self._add_error(f"User Story '{relative_path}' имеет неправильный формат assignee. Ожидается формат: assignee:: `[[@Agent Name]]`", md_file)

        except Exception as e:
            self._add_warning(f"Could not validate assignee correctness for '{md_file}': {e}")

    def validate_readme_title(self, md_file: Path):
        """Проверяет, что все README.md файлы имеют свойство title::."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            filename = Path(relative_path).name
            
            # Проверяем только файлы с именем README.md
            if filename == "README.md":
                content = md_file.read_text(encoding="utf-8")
                
                # Проверяем наличие свойства title::
                if "title::" not in content:
                    self._add_error(f"README.md файл '{relative_path}' не имеет свойства 'title::'", md_file)

        except Exception as e:
            self._add_warning(f"Could not validate README title for '{md_file}': {e}")

    def validate_temporary_artifacts(self, md_file: Path):
        """Проверяет, что файлы с 'сырыми' выводами команд не сохраняются в pages/."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            filename = Path(relative_path).name
            
            # Проверяем только файлы в директории pages
            if not relative_path.startswith("pages/"):
                return
            
            # Проверяем файлы, которые являются "сырыми" выводами команд
            # Примеры: raw.md, error.errors
            raw_command_output_patterns = [
                "raw.md", "error.errors"
            ]
            
            if filename in raw_command_output_patterns:
                self._add_error(f"Файл '{relative_path}' является временным артефактом и не должен сохраняться в pages/", md_file)

        except Exception as e:
            self._add_warning(f"Could not validate temporary artifacts for '{md_file}': {e}")

    def validate_misplaced_files(self):
        """Проверяет, что markdown файлы находятся в разрешенных директориях."""
        try:
            # Сканируем все markdown файлы в проекте
            all_md_files = list(self.base_path.rglob("*.md"))
            
            # Фильтруем файлы, игнорируемые по .gitignore
            all_md_files = [f for f in all_md_files if not self._is_ignored(f)]
            
            for md_file in all_md_files:
                try:
                    relative_path = md_file.relative_to(self.base_path).as_posix()
                    
                    # Проверяем, находится ли файл в разрешенной директории
                    is_in_allowed_dir = any(
                        relative_path.startswith(allowed_dir + "/")
                        for allowed_dir in KNOWLEDGE_BASE_DIRS
                    )
                    
                    # Проверяем, является ли файл разрешенным в корне
                    is_allowed_root_file = relative_path in ALLOWED_ROOT_FILES
                    
                    # Проверяем, находится ли файл в .roo/rules/
                    is_in_rules_dir = relative_path.startswith(".roo/rules/")
                    
                    # Файл разрешен, если он в одной из разрешенных директорий
                    # или является разрешенным файлом в корне
                    if not (is_in_allowed_dir or is_allowed_root_file or is_in_rules_dir):
                        self._add_error(f"Файл '{relative_path}' находится вне разрешенных директорий. "
                                         f"Разрешенные директории: {', '.join(KNOWLEDGE_BASE_DIRS)}, .roo/rules/, "
                                         f"разрешенные файлы в корне: {', '.join(ALLOWED_ROOT_FILES)}", md_file)
                except ValueError:
                    # Если не удалось получить относительный путь, пропускаем файл
                    continue
        except Exception as e:
            self._add_warning(f"Не удалось выполнить проверку misplaced files: {e}")

    def run_validation(self):
        """Запускает все проверки для базы знаний."""
        print(f"Корень проекта: {self.base_path}")
        all_md_files = self._find_markdown_files()
        
        if not all_md_files:
            self._add_warning("Не найдено ни одного markdown-файла для валидации.")
            return

        print(f"\nНайдено {len(all_md_files)} файлов. Собираю имена всех страниц...")
        all_page_names = self._get_all_page_names(all_md_files)
        
        print("Запуск валидации целостности ссылок...")
        for md_file in all_md_files:
            self.validate_link_integrity(md_file, all_page_names)
        
        print("Запуск валидации правильного форматирования ссылок...")
        for md_file in all_md_files:
            self.validate_correct_link_formatting(md_file)
        
        print("Запуск валидации структуры файлов...")
        for md_file in all_md_files:
            self.validate_file_structure(md_file)
        
        print("Запуск валидации схемы свойств...")
        for md_file in all_md_files:
            self.validate_properties_schema(md_file)
        
        print("Запуск валидации правильности статусов...")
        for md_file in all_md_files:
            self.validate_status_correctness(md_file)
        
        print("Запуск валидации правильности assignee...")
        for md_file in all_md_files:
            self.validate_assignee_correctness(md_file)
        
        print("Запуск валидации заголовков в README...")
        for md_file in all_md_files:
            self.validate_readme_title(md_file)
        
        print("Запуск валидации временных артефактов...")
        for md_file in all_md_files:
            self.validate_temporary_artifacts(md_file)
        
        print("Запуск валидации misplaced файлов...")
        self.validate_misplaced_files()
        
        print("Валидация завершена.")


    def print_report(self):
        """Выводит итоговый отчет о найденных ошибках и предупреждениях."""
        print("\n--- Отчет о валидации ---")
        
        # Логируем все ошибки и предупреждения
        for warning in self.warnings:
            self.logger.info(f"WARNING: {warning}")
        
        for error in self.errors:
            self.logger.info(f"ERROR: {error}")
        
        # Логируем отфильтрованные ссылки
        for filtered_link in self.filtered_links:
            self.logger.info(f"FILTERED: {filtered_link}")
        
        if not self.terminal_errors and not self.warnings:
            print("\n✅ Все проверки успешно пройдены! Ошибок не найдено.")
            if self.filtered_links:
                print(f"ℹ️  Отфильтровано концептуальных ссылок: {len(self.filtered_links)}")
                print("   (Отфильтрованные ссылки залогированы в файле логов)")
            return

        if self.warnings:
            print(f"\n⚠️  Найдено предупреждений: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  - {warning}")

        # Показываем только терминальные ошибки в консоли
        if self.terminal_errors:
            print(f"\n❌ Найдено ошибок: {len(self.terminal_errors)}")
            for error in self.terminal_errors:
                print(f"  - {error}")
        
        # Информируем о внешних ошибках, но не показываем их в деталях
        if self.external_errors:
            external_count = len(self.external_errors)
            print(f"\n📁 Найдено {external_count} ошибок в файлах вне директорий базы знаний.")
            print("   Эти ошибки залогированы но не отображаются в терминале.")
        
        # Информируем об отфильтрованных ссылках
        if self.filtered_links:
            print(f"\nℹ️  Отфильтровано концептуальных ссылок: {len(self.filtered_links)}")
            print("   (Отфильтрованные ссылки залогированы в файле логов)")
        
        print("\n-------------------------")


def main():
    parser = argparse.ArgumentParser(description='Скрипт для Валидации Базы Знаний Logseq.')
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path.cwd(),
        help='Корневая директория проекта для валидации.'
    )
    args = parser.parse_args()

    validator = KBValidator(args.project_root)
    validator.run_validation()
    validator.print_report()

    if validator.errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()