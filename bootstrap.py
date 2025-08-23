# /path/to/your/roo-project-template/bootstrap.py
import subprocess
import sys
import shutil
import tempfile
import argparse
from pathlib import Path

# --- КОНФИГУРАЦИЯ ---
PROTECTED_ITEMS = {".git", ".gitignore", ".env", "pyproject.toml", "uv.lock", "README.md", "pages", "journals", "assets", "logseq"}
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

    print("\n🎉 Процесс завершен!")
    print("➡️  Рекомендуется запустить `uv run python scripts/development/generate_logseq_config.py` для обновления конфигурации графа.")

if __name__ == "__main__":
    main()