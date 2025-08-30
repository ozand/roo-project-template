---
description: "Автоматически собрать итоговый отчет по завершенной фазе, а затем запустить процесс извлечения уроков."
---
<task>
    <name>Ретроспектива, Закрытие Фазы и Извлечение Уроков</name>
    <objective>Автоматически собрать итоговый отчет по завершенной фазе, а затем запустить процесс извлечения уроков для анализа результатов и планирования следующей фазы.</objective>
    <trigger>Все User Stories, относящиеся к определенной фазе, получают статус `[[DONE]]`.</trigger>
    <context>
        <knowledge_base>Все файлы `STORY-*.md` со свойством `phase:: [[Phase-X]]`.</knowledge_base>
        <standard>[[rules.04-filename-referencing-rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Сбор и анализ данных для ретроспективы">
            <instruction>Делегировать задачу агенту `Project Research`.</instruction>
            <sub_task_prompt>
"**Задача:** Подготовь отчет о завершении Фазы [[Phase-X]].
1. Используя Datalog-запрос, найди все User Stories, относящиеся к этой фазе.
2. Собери статистику: общее количество задач, распределение по категориям (API, UI, INFRA), распределение по приоритетам.
3. Создай новую страницу `pages/reports.phase-[X]-summary.md` и заполни ее собранной статистикой и списком всех завершенных задач."
            </sub_task_prompt>
            <on_failure>
                <instruction>Сообщить пользователю, что не удалось собрать отчет по ретроспективе. Предоставить лог ошибки от `Project Research`.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Информирование о готовности отчета">
            <instruction>Сообщить пользователю о готовности отчета по ретроспективе и о начале процесса извлечения уроков.</instruction>
        </step>
        <step id="3" name="Запуск извлечения уроков">
            <instruction>Инициировать выполнение команды `[[commands.extract-phase-learnings]]`.</instruction>
            <on_failure>
                <instruction>Сообщить пользователю, что не удалось запустить процесс извлечения уроков.</instruction>
            </on_failure>
        </step>
    </workflow>
</task>