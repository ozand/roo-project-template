---
description: "Последовательно реализовать все User Stories, определенные в плане реализации для текущей фазы проекта."
---
<task>
    <name>Начало Цикла Разработки по Плану</name>
    <objective>Последовательно реализовать все User Stories, определенные в плане реализации для текущей фазы проекта.</objective>
    <trigger>Успешное завершение задачи "Инициация Фазы Разработки" и наличие утвержденного `implementation-plan`.</trigger>
    <context>
        <implementation_plan>[[pages/phase-[X]-implementation-plan]]</implementation_plan>
        <standard>[[rules.04-filename_referencing_rules]]</standard>
    </context>
    <workflow>
        <step id="1" name="Определение списка задач">
            <instruction>Проанализировать документ `<implementation_plan>` и извлечь из него полный, упорядоченный список User Stories (`[[STORY-ID]]`), подлежащих реализации в этой фазе.</instruction>
            <tool_to_use>read</tool_to_use>
            <on_failure>
                <instruction>Сообщить пользователю, что не удалось прочитать план реализации или извлечь из него список задач.</instruction>
            </on_failure>
        </step>
        <step id="2" name="Последовательная реализация">
            <instruction>Для каждой User Story из полученного списка, в строгом порядке, делегировать задачу на реализацию агенту `Code`.</instruction>
            <sub_task_prompt_template>
"**Задача:** Реализуй User Story `[[STORY-ID]]`.
**Контекст:**
- Детальное описание и критерии приемки находятся в файле `[[STORY-ID]]`.
- Технические спецификации и зависимости описаны в `[[implementation_plan]]`.
- Всегда следуй стандартам кодирования из `[[rules.01-quality_guideline]]`.
**Протокол:**
1. Перед началом работы измени свойство `status` в файле `[[STORY-ID]]` на `[[DOING]]`.
2. После завершения реализации и прохождения тестов, измени свойство `status` на `[[DONE]]`.
3. Создай ссылки на все измененные или созданные файлы кода в документе `[[STORY-ID]]`."
            </sub_task_prompt_template>
            <on_failure>
                <instruction>Сообщить пользователю о сбое при реализации `[[STORY-ID]]`. Предоставить лог от агента `Code` и приостановить цикл разработки до решения проблемы.</instruction>
            </on_failure>
        </step>
        <step id="3" name="Завершение фазы">
            <instruction>После того, как все User Stories из списка будут выполнены (получат статус `[[DONE]]`), инициировать задачу "Ретроспектива и Закрытие Фазы".</instruction>
        </step>
    </workflow>
</task>