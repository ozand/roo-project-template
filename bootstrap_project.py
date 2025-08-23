# /path/to/your/roo-project-template/bootstrap_project.py
import subprocess
import sys
from pathlib import Path

# --- КОНФИГУРАЦИЯ ---
# Ожидаемые директории, которые должны прийти из шаблона GitHub
EXPECTED_DIRS = [".roo/rules", "scripts/development"]

def run_command(command, cwd):
    """Выполняет команду в терминале и выводит результат."""
    print(f"\n> Запуск команды: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"❌ Ошибка выполнения:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    print(result.stdout)
    print("✅ Успешно.")
    return result

def bootstrap_project():
    """
    Выполняет полную инициализацию проекта ПОСЛЕ его создания из шаблона GitHub.
    """
    project_root = Path.cwd()
    print(f"Инициализация проекта в: {project_root}\n")

    # --- Шаг 1: Проверка, что мы в правильном месте ---
    print("--- Шаг 1: Проверка структуры проекта ---")
    all_ok = True
    for dir_path in EXPECTED_DIRS:
        if not (project_root / dir_path).is_dir():
            print(f"❌ Ошибка: Директория '{dir_path}' не найдена. Убедитесь, что репозиторий создан из шаблона.")
            all_ok = False
    if not all_ok:
        sys.exit(1)
    print("✅ Структура шаблона корректна.")

    # --- Шаг 2: Инициализация Python-окружения через uv ---
    print("\n--- Шаг 2: Инициализация Python и uv ---")
    run_command(["uv", "init", "--quiet"], cwd=project_root)
    run_command(["uv", "venv"], cwd=project_root)
    # Здесь можно добавить установку базовых зависимостей, если нужно
    # run_command(["uv", "pip", "install", "pytest"], cwd=project_root)
    
    # --- Шаг 3: Создание символических ссылок для правил ---
    print("\n--- Шаг 3: Создание символических ссылок для Logseq ---")
    # Для Windows лучше использовать PowerShell
    if sys.platform == "win32":
        ps_script_path = project_root / "scripts" / "development" / "create_logseq_links.ps1"
        if ps_script_path.exists():
             run_command(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script_path)], cwd=project_root)
        else:
            print("⚠️  Предупреждение: Скрипт для создания симлинков не найден.")
    # Для Linux/macOS можно использовать python
    else:
        # Здесь может быть вызов python-скрипта для symlink
        pass

    # --- Шаг 4: Генерация config.edn для Logseq ---
    print("\n--- Шаг 4: Генерация config.edn для чистоты графа ---")
    config_script = project_root / "scripts" / "development" / "generate_logseq_config.py"
    if config_script.exists():
        run_command(["uv", "run", "python", str(config_script)], cwd=project_root)
    else:
        print("⚠️  Предупреждение: Скрипт генерации config.edn не найден.")

    print("\n🎉 Проект успешно инициализирован и готов к работе!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--init', action='store_true', help='Run full project initialization.')
    args = parser.parse_args()

    if args.init:
        bootstrap_project()
    else:
        print("Пожалуйста, используйте флаг --init для запуска полной инициализации проекта.")