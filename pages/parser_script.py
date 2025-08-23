import os
import re

# --- НАСТРОЙКИ ---
# Имя исходного файла, который нужно обработать
INPUT_FILE = "raw.md"
# НОВОЕ: Имя подпапки для сохранения результатов
OUTPUT_SUBDIR = "memory-bank"

# Имена файлов, которые мы ожидаем найти и создать
EXPECTED_FILENAMES = [
    "gap.md",
    "requirements.md",
    "backlog.md",
    "roadmap.md",
    "sprint-plan.md",
    "documentation-maintenance.md",
]
# --- КОНЕЦ НАСТРОЕК ---


def parse_raw_file():
    """
    Основная функция для анализа файла raw.md и создания отдельных файлов.
    """
    print(f"--- Запуск скрипта обработки файла {INPUT_FILE} ---")

    if not os.path.exists(INPUT_FILE):
        print(f"ОШИБКА: Файл '{INPUT_FILE}' не найден в этой папке.")
        print("Пожалуйста, убедитесь, что файл находится рядом со скриптом.")
        return

    # НОВОЕ: Создаем подпапку для результатов, если она еще не существует.
    # exist_ok=True предотвращает ошибку, если папка уже создана.
    try:
        os.makedirs(OUTPUT_SUBDIR, exist_ok=True)
        print(f"Результаты будут сохранены в папку: '{OUTPUT_SUBDIR}/'")
    except OSError as e:
        print(f"ОШИБКА: Не удалось создать папку '{OUTPUT_SUBDIR}': {e}")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"(`([a-z-]+.md)`|([A-Z][a-zA-Z\s_`]+\(`([a-z-]+.md)`\)))"
        r".*?"
        r"```markdown\n"
        r"(.*?)\n"
        r"```",
        re.DOTALL,
    )

    matches = pattern.findall(content)

    if not matches:
        print(
            "ОШИБКА: Не найдено ни одного блока документации в формате ```markdown...```."
        )
        return

    found_count = 0
    for match in matches:
        filename = next(
            (name for name in [match[1], match[3]] if name and name.endswith(".md")), None
        )

        if filename and filename in EXPECTED_FILENAMES:
            file_content = match[4].strip()

            print(f"Найден документ: {filename}. Создание файла...")

            # ИЗМЕНЕНО: Формируем полный путь к файлу, включая подпапку.
            # os.path.join() корректно соединяет пути для любой ОС.
            full_path = os.path.join(OUTPUT_SUBDIR, filename)

            try:
                # ИЗМЕНЕНО: Записываем файл по новому, полному пути.
                with open(full_path, "w", encoding="utf-8") as f_out:
                    f_out.write(file_content)
                # ИЗМЕНЕНО: В сообщении указываем полный путь.
                print(f"  [+] Файл '{full_path}' успешно создан.")
                found_count += 1
            except OSError as e:
                print(f"  [!] ОШИБКА при записи файла '{full_path}': {e}")

    print(
        f"--- Завершено. Создано {found_count} из {len(EXPECTED_FILENAMES)} ожидаемых файлов. ---"
    )


if __name__ == "__main__":
    parse_raw_file()
    os.system("pause")
