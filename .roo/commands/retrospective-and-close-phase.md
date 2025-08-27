---
description: "Автоматически собрать итоговый отчет по завершенной фазе разработки для анализа результатов и планирования следующей фазы"
---

<task>
    <name>Ретроспектива и Закрытие Фазы</name>
    <objective>Автоматически собрать итоговый отчет по завершенной фазе разработки для анализа результатов и планирования следующей фазы.</objective>
    <trigger>Все User Stories, относящиеся к определенной фазе, получают статус `[[DONE]]`.</trigger>
    <context>
        <knowledge_base>Все файлы `STORY-*.md` со свойством `phase:: [[Phase-X]]`.</knowledge_base>
        <standard>[[rules.knowledge-base-standard]]</standard>
    </context>
    <workflow>
        <step id="1" name="Сбор и анализ данных">
            <instruction>Делегировать задачу агенту `Project Research`.</instruction>
            <sub_task_prompt>
"**Задача:** Подготовь отчет о завершении Фазы [Номер Фазы].
1. Используя Datalog-запрос, найди все User Stories, относящиеся к этой фазе.
2. Собери статистику: общее количество задач, распределение по категориям (API, UI, INFRA), распределение по приоритетам.
3. Создай новую страницу `pages/reports.phase-[X]-summary.md` и заполни ее собранной статистикой и списком всех завершенных задач."
            </sub_task_prompt>
        </step>
        <step id="2" name="Информирование">
            <instruction>Сообщить пользователю о готовности отчета по ретроспективе.</instruction>
        </step>
    </workflow>
</task>