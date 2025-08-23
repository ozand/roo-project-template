# /path/to/your/roo-project-template/migrate_project_to_standard.py
import shutil
from pathlib import Path
import argparse

def migrate_project(project_root: Path, template_root: Path):
    """
    Выполняет миграцию существующего проекта к новому стандарту базы знаний.
    1. Копирует эталонные файлы (правила, скрипты) из шаблона.
    2. Перемещает существующую документацию в папку pages/.
    """
    print(f"Запуск миграции для проекта: {project_root}")
    print(f"Используется шаблон из: {template_root}\n")

    # --- Шаг 1: Бутстраппинг - копирование эталонных файлов ---
    print("--- Этап 1: Копирование стандартных файлов и правил ---")
    
    dirs_to_copy = [".roo", "scripts"]
    for dir_name in dirs_to_copy:
        source_dir = template_root / dir_name
        target_dir = project_root / dir_name

        if not source_dir.is_dir():
            print(f"⚠️  Предупреждение: Директория шаблона '{dir_name}' не найдена. Пропускаю.")
            continue
        
        if target_dir.exists():
            print(f"⚠️  Директория '{dir_name}' уже существует в проекте. Пропускаю копирование.")
        else:
            try:
                shutil.copytree(source_dir, target_dir)
                print(f"✅ Директория '{dir_name}' успешно скопирована.")
            except Exception as e:
                print(f"❌ Ошибка при копировании '{dir_name}': {e}")

    # --- Шаг 2: Миграция - перемещение существующей документации ---
    print("\n--- Этап 2: Миграция существующей документации в pages/ ---")
    
    target_pages_dir = project_root / "pages"
    target_pages_dir.mkdir(exist_ok=True)
    
    # Определяем папки, откуда нужно мигрировать файлы
    migration_sources = [
        project_root / "docs" / "memory-bank",
        project_root / "docs" / "memory-bank" / "user_story"
    ]
    
    migrated_files_count = 0
    for source_dir in migration_sources:
        if not source_dir.is_dir():
            print(f"ℹ️  Директория для миграции не найдена, пропускаю: {source_dir.relative_to(project_root)}")
            continue
        
        print(f"Сканирование '{source_dir.relative_to(project_root)}'...")
        for file_path in source_dir.glob("*.md"):
            target_file_path = target_pages_dir / file_path.name
            
            if target_file_path.exists():
                print(f"  - ⚠️  Файл '{file_path.name}' уже существует в pages/. Пропускаю.")
            else:
                try:
                    shutil.move(str(file_path), str(target_file_path))
                    print(f"  - ✅ Перемещен файл: {file_path.name}")
                    migrated_files_count += 1
                except Exception as e:
                    print(f"  - ❌ Ошибка при перемещении '{file_path.name}': {e}")

    print(f"\nВсего перемещено файлов: {migrated_files_count}")
    
    # --- Шаг 3: Создание пустых директорий, если их нет ---
    print("\n--- Этап 3: Проверка наличия обязательных папок Logseq ---")
    dirs_to_create = ["journals", "assets", "logseq"]
    for dir_name in dirs_to_create:
        (project_root / dir_name).mkdir(exist_ok=True)
        print(f"✅ Проверена/создана директория: {dir_name}")

    print("\n🎉 Миграция проекта успешно завершена!")
    print("➡️  Следующий шаг: запустите `uv run python scripts/development/generate_logseq_config.py` для настройки графа.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скрипт для миграции существующего проекта к стандарту Logseq KB.")
    parser.add_argument(
        "--template-path",
        type=Path,
        required=True,
        help="Абсолютный или относительный путь к репозиторию roo-project-template."
    )
    
    args = parser.parse_args()
    
    current_project_path = Path.cwd()
    template_path = args.template_path.resolve()

    if not template_path.is_dir():
        print(f"❌ Ошибка: Указанный путь к шаблону не существует или не является директорией: {template_path}")
        sys.exit(1)

    migrate_project(current_project_path, template_path)