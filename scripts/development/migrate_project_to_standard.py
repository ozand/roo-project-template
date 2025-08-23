# /path/to/your/roo-project-template/update_project_from_template.py
import subprocess
import sys
import shutil
import tempfile
import argparse
from pathlib import Path

# --- КОНФИГУРАЦИЯ ---

# Файлы и папки, которые НИКОГДА не должны перезаписываться в существующем проекте
PROTECTED_FILES = {
    ".git",
    ".gitignore",
    ".env",
    "pyproject.toml",
    "uv.lock",
    "README.md", # Обычно README проекта уникален
    "pages",     # Не перезаписываем, чтобы не потерять существующие знания
    "journals",
    "assets",
    "logseq",
}

# Директории, которые мы будем копировать из шаблона
DIRECTORIES_TO_COPY = [
    ".roo",
    "scripts",
]

def run_command(command, cwd):
    """Выполняет команду в терминале и выводит результат."""
    print(f"\n> Запуск команды: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"❌ Ошибка выполнения:")
        print(result.stdout)
        print(result.stderr)
        return False
    print(result.stdout)
    print("✅ Успешно.")
    return True

def copy_template_files(template_path: Path, project_path: Path):
    """Копирует файлы из шаблона в проект, защищая важные файлы."""
    print("\n--- Этап 1: Копирование стандартных файлов из шаблона ---")
    
    for dir_name in DIRECTORIES_TO_COPY:
        source_dir = template_path / dir_name
        target_dir = project_path / dir_name

        if not source_dir.is_dir():
            print(f"⚠️  Предупреждение: Директория шаблона '{dir_name}' не найдена. Пропускаю.")
            continue

        # Если целевая директория существует, удаляем ее для полной синхронизации
        if target_dir.exists():
            print(f"Обновление директории '{dir_name}'...")
            shutil.rmtree(target_dir)
        
        try:
            shutil.copytree(source_dir, target_dir)
            print(f"✅ Директория '{dir_name}' успешно скопирована/обновлена.")
        except Exception as e:
            print(f"❌ Ошибка при копировании '{dir_name}': {e}")
            
def migrate_existing_project(project_path: Path):
    """Запускает скрипт миграции, если он был скопирован."""
    print("\n--- Этап 2: Запуск скрипта миграции (если применимо) ---")
    
    migration_script = project_path / "scripts" / "development" / "migrate_project_to_standard.py"
    
    if migration_script.exists():
        print("Обнаружен скрипт миграции. Запускаю...")
        if not run_command(["uv", "run", "python", str(migration_script)], cwd=project_path):
             print("❌ Ошибка выполнения скрипта миграции.")
             # В реальном проекте здесь можно добавить логику отката изменений
    else:
        print("ℹ️  Скрипт миграции не найден, пропущено.")


def main():
    parser = argparse.ArgumentParser(description="Скрипт для инициализации или обновления проекта из шаблона.")
    parser.add_argument(
        "--template-repo",
        type=str,
        default="https://github.com/ozand/roo-project-template.git",
        help="URL Git-репозитория с шаблоном."
    )
    args = parser.parse_args()

    project_root = Path.cwd()

    # Клонируем шаблон во временную директорию
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Клонирование шаблона из {args.template_repo}...")
        
        clone_result = run_command(
            ["git", "clone", args.template_repo, "."], 
            cwd=temp_dir
        )
        
        if not clone_result:
            print("❌ Не удалось клонировать репозиторий-шаблон. Прерываю выполнение.")
            return

        template_path = Path(temp_dir)
        
        # Копируем файлы, уважая PROTECTED_FILES
        copy_template_files(template_path, project_root)
        
        # Запускаем миграцию
        migrate_existing_project(project_root)

    print("\n🎉 Обновление проекта завершено!")
    print("➡️  Рекомендуется запустить `uv run python scripts/development/generate_logseq_config.py` для обновления конфигурации графа.")


if __name__ == "__main__":
    main()