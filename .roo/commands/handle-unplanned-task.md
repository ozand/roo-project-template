---
description: "Корректно задокументировать и интегрировать в текущий план новую задачу (баг, доработка), которая не была предусмотрена изначально."
---

<task>
    <name>Обработка Незапланированной Задачи</name>
    <objective>Корректно задокументировать и интегрировать в текущий план новую задачу (баг, доработка), которая не была предусмотрена изначально.</objective>
    <trigger>Получение от пользователя отчета о баге или запроса на новую фичу.</trigger>
    <context>
        <user_input>[Здесь вставляется текст отчета о баге или описание новой фичи]</user_input>
        <standard>[[rules.knowledge-base-standard]]</standard>
    </context>
    <workflow>
        <step id="1" name="Создание и документирование">
            <instruction>Делегировать задачу агенту `User Story Creator`.</instruction>
            <sub_task_prompt>
"**Задача:** На основе предоставленных данных, создай новый файл `pages/STORY-[DEFECT/FEATURE]-[ID].md`. Опиши User Story, Acceptance Criteria и заполни все обязательные свойства (`type`, `status`, `priority`)."
            </sub_task_prompt>
        </step>
        <step id="2" name="Интеграция в план">
            <instruction>Делегировать задачу агенту `Architect`.</instruction>
            <sub_task_prompt>
"**Задача:** Проанализируй новую User Story `[[ID_НОВОЙ_ЗАДАЧИ]]`. Найди наиболее подходящий эпик (`[[EPIC-...]]`) и требование (`[[REQ-...]]`) и свяжи их с новой задачей через свойства. Если подходящих нет, создай отчет для Product Owner. Оцени влияние новой задачи на текущий `sprint-plan`."
            </sub_task_prompt>
        </step>
    </workflow>
</task>