# /path/to/your/roo-project-template/bootstrap.py
import subprocess
import sys
import shutil
import tempfile
import argparse
import os
from pathlib import Path

# --- КОНФИГУРАЦИЯ ---
# Директории, которые копируются из шаблона
TEMPLATE_DIRS_TO_COPY = [".roo", "scripts", "pages"]
# Директории для миграции старых документов
MIGRATION_SOURCE_DIRS = ["docs/memory-bank", "docs/memory-bank/user_story"]

def run_command(command, cwd):
    print(f"\n> Запуск команды: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"❌ Ошибка выполнения:\n{result.stderr or result.stdout}")
        return False
    print(result.stdout)
    print("✅ Успешно.")
    return True

def copy_template_files(template_path: Path, project_path: Path):
    print("\n--- Этап 1: Копирование/обновление стандартных файлов из шаблона ---")
    for dir_name in TEMPLATE_DIRS_TO_COPY:
        source_dir = template_path / dir_name
        target_dir = project_path / dir_name
        if not source_dir.is_dir():
            print(f"⚠️  Предупреждение: Директория шаблона '{dir_name}' не найдена.")
            continue
        if target_dir.exists() and dir_name != "pages": # Не удаляем pages, чтобы не терять данные
            print(f"Обновление директории '{dir_name}'...")
            shutil.rmtree(target_dir)
        
        try:
            # Копируем содержимое, а не заменяем папку, чтобы безопасно обновить pages
            shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
            print(f"✅ Директория '{dir_name}' успешно скопирована/обновлена.")
        except Exception as e:
            print(f"❌ Ошибка при копировании '{dir_name}': {e}")

def migrate_existing_docs(project_path: Path):
    print("\n--- Этап 2: Миграция существующей документации в pages/ ---")
    target_pages_dir = project_path / "pages"
    target_pages_dir.mkdir(exist_ok=True)
    migrated_count = 0
    for source_rel_path in MIGRATION_SOURCE_DIRS:
        source_dir = project_path / source_rel_path
        if not source_dir.is_dir():
            print(f"ℹ️  Директория для миграции не найдена, пропускаю: {source_rel_path}")
            continue
        print(f"Сканирование '{source_rel_path}'...")
        for file_path in source_dir.glob("*.md"):
            target_file_path = target_pages_dir / file_path.name
            if target_file_path.exists():
                print(f"  - ⚠️  Файл '{file_path.name}' уже существует в pages/. Пропускаю.")
            else:
                try:
                    shutil.move(str(file_path), str(target_file_path))
                    print(f"  - ✅ Перемещен файл: {file_path.name}")
                    migrated_count += 1
                except Exception as e:
                    print(f"  - ❌ Ошибка при перемещении '{file_path.name}': {e}")
    print(f"\nВсего перемещено файлов: {migrated_count}")

def create_symlinks(project_path: Path):
    """
    Создает символические ссылки из pages/ в .roo/ для правил и команд.
    """
    print("\n--- Этап 3: Создание символических ссылок для правил и команд ---")
    
    pages_dir = project_path / "pages"
    link_map = {
        "rules": project_path / ".roo" / "rules",
        "commands": project_path / ".roo" / "commands"
    }

    # 1. Убедиться, что целевые директории существуют
    for target_dir in link_map.values():
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"ℹ️  Директория '{target_dir}' готова.")

    # 2. Найти файлы в pages/ и создать для них ссылки
    files_to_link = list(pages_dir.glob("rules.*.md")) + list(pages_dir.glob("commands.*.md"))
    
    if not files_to_link:
        print("⚠️  Не найдено файлов для создания ссылок в pages/.")
        return

    for source_file in files_to_link:
        parts = source_file.name.split('.', 2) # e.g., ['rules', 'quality-guideline', 'md']
        if len(parts) < 3:
            continue
            
        link_type = parts[0]  # 'rules' or 'commands'
        link_name = parts[1] + ".md" # 'quality-guideline.md'
        
        target_dir = link_map.get(link_type)
        if not target_dir:
            continue
            
        link_path = target_dir / link_name

        # Удаляем старую ссылку/файл, если она существует
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()

        # Создаем новую ссылку
        try:
            # Для Windows может потребоваться administrator privileges (target_is_directory=False)
            # os.symlink() ожидает строки, а не Path объекты в некоторых версиях Python
            os.symlink(str(source_file.resolve()), str(link_path.resolve()))
            print(f"✅ Создана ссылка: '{link_path}' -> '{source_file}'")
        except OSError as e:
            print(f"❌ Ошибка создания ссылки для '{source_file.name}': {e}")
            print("ℹ️  В Windows для создания символических ссылок может потребоваться запуск скрипта от имени Администратора.")
        except Exception as e:
            print(f"❌ Неизвестная ошибка при создании ссылки для '{source_file.name}': {e}")

def main():
    parser = argparse.ArgumentParser(description="Скрипт для инициализации или миграции проекта из шаблона RooCode.")
    parser.add_argument("--migrate", action='store_true', help="Запустить режим миграции для существующего проекта.")
    parser.add_argument("--repo", type=str, default="https://github.com/ozand/roo-project-template.git", help="URL Git-репозитория с шаблоном.")
    args = parser.parse_args()

    project_root = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Клонирование шаблона из {args.repo}...")
        if not run_command(["git", "clone", args.repo, "."], cwd=temp_dir):
            print("❌ Не удалось клонировать репозиторий-шаблон. Прерываю выполнение.")
            return

        template_path = Path(temp_dir)
        copy_template_files(template_path, project_root)

        if args.migrate:
            migrate_existing_docs(project_root)

    # Запускаем создание ссылок после всех операций с файлами
    create_symlinks(project_root)

    print("\n🎉 Процесс завершен!")
    print("➡️  Рекомендуется запустить `uv run python scripts/development/generate_logseq_config.py` для обновления конфигурации графа.")

if __name__ == "__main__":
    main()