---
description: "Провести полный цикл декомпозиции плановых документов в атомарные, готовые к работе артефакты в графе знаний Logseq."
---
<task>
    <name>Инициация Фазы Разработки</name>
    <objective>Провести полный цикл декомпозиции плановых документов в атомарные, готовые к работе артефакты в графе знаний Logseq.</objective>
    <trigger>Начало новой фазы разработки, наличие в `pages/` файлов `roadmap.md`, `backlog.md`, `requirements.md`.</trigger>
    <context>
        <source_documents>[[roadmap]], [[backlog]], [[requirements]]</source_documents>
        <standard>[[rules.04-filename_referencing_rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Декомпозиция требований и задач">
            <instruction>Делегировать задачу агенту `User Story Creator`.</instruction>
            <sub_task_prompt>
"**Задача:** Проанализируй [[backlog]] и [[requirements]]. Для каждой User Story и каждого требования, указанных в этих документах, создай отдельный, атомарный файл в директории `pages/` в соответствии со стандартом. Заполни все обязательные свойства и создай необходимые ссылки."
            </sub_task_prompt>
            <on_failure>
                <instruction>Сообщить пользователю о сбое на этапе декомпозиции. Предоставить лог ошибки от `User Story Creator`.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Планирование реализации">
            <instruction>Делегировать задачу агенту `Architect`.</instruction>
            <sub_task_prompt>
"**Задача:** На основе созданных User Stories и требований, разработай детальный `implementation-plan` для этой фазы. Создай для него отдельную страницу `pages/phase-[X]-implementation-plan.md`. План должен включать последовательность реализации задач и технические спецификации."
            </sub_task_prompt>
            <human_approval_gate>true</human_approval_gate>
            <on_failure>
                <instruction>Сообщить пользователю, что `Architect` не смог создать план реализации. Предоставить лог ошибки.</instruction>
            </on_failure>
        </step>
        <step id="3" name="Финальная валидация">
            <instruction>Запустить скрипт валидации для проверки целостности созданного графа знаний.</instruction>
            <command>uv run python scripts/development/validate_kb.py</command>
            <expected_result>Отсутствие ошибок валидации.</expected_result>
            <on_failure>
                <instruction>Сообщить пользователю, что база знаний не прошла валидацию после декомпозиции. Предоставить отчет из `validation_report.log` и остановить процесс инициации фазы.</instruction>
            </on_failure>
        </step>
    </workflow>
</task>