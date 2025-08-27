# /path/to/your/roo-project-template/bootstrap.py
import subprocess
import sys
import shutil
import tempfile
import argparse
import os
from pathlib import Path

# --- КОНФИГУРАЦИЯ ---
TEMPLATE_DIRS_TO_COPY = [".roo", "scripts"]
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
        if target_dir.exists():
            print(f"Обновление директории '{dir_name}'...")
            shutil.rmtree(target_dir)
        try:
            shutil.copytree(source_dir, target_dir)
            print(f"✅ Директория '{dir_name}' успешно скопирована.")
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

def create_symlinks_in_pages(project_path: Path):
    """
    Создает символические ссылки В pages/ ИЗ .roo/ для правил и команд.
    """
    print("\n--- Этап 3: Создание символических ссылок в pages/ ---")
    
    pages_dir = project_path / "pages"
    pages_dir.mkdir(exist_ok=True)
    
    source_dirs = {
        "rules": project_path / ".roo" / "rules",
        "commands": project_path / ".roo" / "commands"
    }

    for link_type, source_dir in source_dirs.items():
        if not source_dir.is_dir():
            print(f"⚠️  Директория-источник не найдена, пропускаю: {source_dir}")
            continue
        
        for source_file in source_dir.glob("*.md"):
            # Создаем имя для ссылки с неймспейсом, например, "rules.quality-guideline.md"
            link_name_parts = source_file.stem.split('-', 1)
            if len(link_name_parts) > 1 and link_name_parts[0].isdigit():
                 # Убираем цифровой префикс типа "01-"
                link_stem = link_name_parts[1]
            else:
                link_stem = source_file.stem

            link_name = f"{link_type}.{link_stem}.md"
            link_path = pages_dir / link_name

            if link_path.exists() or link_path.is_symlink():
                link_path.unlink()

            try:
                os.symlink(str(source_file.resolve()), str(link_path.resolve()))
                print(f"✅ Создана ссылка: '{link_path}' -> '{source_file}'")
            except OSError as e:
                print(f"❌ Ошибка создания ссылки для '{source_file.name}': {e}")
                print("ℹ️  В Windows для создания символических ссылок может потребоваться запуск скрипта от имени Администратора.")
            except Exception as e:
                print(f"❌ Неизвестная ошибка при создании ссылки для '{source_file.name}': {e}")

def main():
    parser = argparse.ArgumentParser(description="Скрипт для инициализации или миграции проекта из шаблона RooCode.")
    # ... (аргументы без изменений)
    args = parser.parse_args()
    project_root = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        # ... (код клонирования без изменений)
        template_path = Path(temp_dir)
        copy_template_files(template_path, project_root)
        if args.migrate:
            migrate_existing_docs(project_root)

    create_symlinks_in_pages(project_root)

    print("\n🎉 Процесс завершен!")
    # ... (остальные сообщения без изменений)

if __name__ == "__main__":
    main()