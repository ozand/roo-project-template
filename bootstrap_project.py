# /path/to/your/roo-project-template/bootstrap_project.py
import shutil
from pathlib import Path

# --- КОНФИГУРАЦИЯ ШАБЛОНА ---
# Определяем, где находится сам шаблон (относительно этого скрипта)
TEMPLATE_ROOT = Path(__file__).parent.resolve()

# --- НОВОЕ: "Белый список" директорий для копирования ---
# Эти папки будут скопированы из шаблона в новый проект целиком.
DIRECTORIES_TO_COPY = [
    ".roo",
    "scripts",
]

# Эти папки будут просто созданы пустыми
DIRECTORIES_TO_CREATE = [
    "pages",
    "journals",
    "assets",
    "logseq",
]

def bootstrap_project(target_root: Path):
    """
    Создает структуру папок и рекурсивно копирует эталонные директории
    из репозитория-шаблона в целевой проект.
    """
    print(f"Инициализация структуры проекта в: {target_root}\n")

    # --- Шаг 1: Копирование директорий с файлами ---
    print("Копирование эталонных директорий...")
    for dir_name in DIRECTORIES_TO_COPY:
        source_dir = TEMPLATE_ROOT / dir_name
        target_dir = target_root / dir_name

        if source_dir.is_dir():
            try:
                shutil.copytree(source_dir, target_dir)
                print(f"✅ Директория '{dir_name}' успешно скопирована.")
            except FileExistsError:
                print(f"⚠️  Директория '{dir_name}' уже существует. Пропускаю.")
            except Exception as e:
                print(f"❌ Ошибка при копировании '{dir_name}': {e}")
        else:
            print(f"⚠️  Предупреждение: Исходная директория не найдена: {source_dir}")

    # --- Шаг 2: Создание пустых директорий ---
    print("\nСоздание пустых директорий для Logseq...")
    for dir_name in DIRECTORIES_TO_CREATE:
        target_dir = target_root / dir_name
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Создана/проверена директория: {dir_name}")
        except Exception as e:
            print(f"❌ Ошибка при создании '{dir_name}': {e}")

    print("\n🎉 Инициализация проекта успешно завершена!")
    print("Не забудьте запустить `uv run python scripts/development/generate_logseq_config.py` для настройки графа.")

if __name__ == "__main__":
    # Скрипт будет запущен в директории нового проекта
    new_project_path = Path.cwd()
    bootstrap_project(new_project_path)