---
description: "Выявить и устранить расхождения между фактическим состоянием реализации в Git и документированным состоянием в базе знаний Logseq."
---

<task>
    <name>Аудит и Синхронизация Базы Знаний</name>
    <objective>Выявить и устранить расхождения между фактическим состоянием реализации в Git и документированным состоянием в базе знаний Logseq.</objective>
    <trigger>По расписанию (еженедельно) или по ручному запуску.</trigger>
    <context>
        <knowledge_base>Все файлы `STORY-*.md` в директории `pages/`.</knowledge_base>
        <source_of_truth_code>Логи Git-коммитов в текущей ветке.</source_of_truth_code>
        <standard>[[rules.knowledge-base-standard]]</standard>
    </context>
    <workflow>
        <step id="1" name="Анализ расхождений">
            <instruction>Делегировать задачу агенту `Project Research`.</instruction>
            <sub_task_prompt>
"**Задача:** Провести аудит. 
1. Найди все User Stories со статусом `[[DONE]]`, для которых нет соответствующего коммита в Git (с ID истории в сообщении).
2. Найди все User Stories со статусом `[[TODO]]` или `[[DOING]]`, для которых уже существует коммит о закрытии.
3. Сформируй отчет о всех найденных расхождениях в моем `journal` за сегодня."
            </sub_task_prompt>
        </step>
        <step id="2" name="Запрос на исправление">
            <instruction>На основе отчета от `Project Research`, запросить у пользователя подтверждение на исправление статусов в файлах `STORY-*.md`.</instruction>
            <tool_to_use>ask_followup_question</tool_to_use>
        </step>
        <step id="3" name="Исправление">
            <instruction>После получения подтверждения, делегировать агенту `Code` задачу по исправлению статусов.</instruction>
            <sub_task_prompt>
"**Задача:** Внеси исправления в свойство `status` в следующих файлах User Story согласно отчету об аудите: [список файлов]."
            </sub_task_prompt>
        </step>
    </workflow>
</task>