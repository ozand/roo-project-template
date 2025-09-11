# Гайдлайн: как всем проектам/AI-агентам работать с централизованным Prefect Server

**Сервер:** UI и API — `http://192.168.1.35:4200` → API: `http://192.168.1.35:4200/api`
**Пул воркеров:** `docker-pool` (уже создан и запущен на сервере)

---

## 1) Базовая настройка клиента/проекта

На каждой машине (CI, dev-ноут, сервер с агентом) один раз:

```bash
prefect config set PREFECT_API_URL=http://192.168.1.35:4200/api
prefect config view | grep PREFECT_API_URL
```

> НИКОГДА не запускайте локально `prefect server start` — все ходят в централизованный сервер.

---

## 2) Быстрый шаблон проекта (минимум кода)

```python
# flows/hello.py
from prefect import flow, task

@task
def say(name: str): print(f"Hello, {name}!")

@flow
def hello_flow(name: str = "world"):
    say(name)
```

---

## 3) Деплой (рекомендуется через образ Docker)

**Вариант A — “образ с кодом” (прод-подход):**

1. Соберите образ с проектом:

```bash
docker build -t your-registry/your-app:latest .
docker push your-registry/your-app:latest
```

2. Создайте «манифест» деплоя (корень проекта → `prefect.yaml`):

```yaml
# prefect.yaml
profiles:
  default:
    api_url: http://192.168.1.35:4200/api

deployments:
  - name: hello
    entrypoint: flows/hello.py:hello_flow
    pool: docker-pool
    job_variables:
      image: your-registry/your-app:latest
      env:
        PREFECT_LOGGING_LEVEL: INFO
```

3. Примените деплой:

```bash
prefect deploy --name hello --apply
# или (если несколько деплоев в файле)  prefect deploy --all --apply
```

**Вариант B — “код из Git”:** создайте Git-block и укажите `job_variables` для `image` (например, `prefecthq/prefect:3-latest`) + параметры доступа к репо. Этот вариант удобен для быстрых прототипов без сборки образа.

---

## 4) Запуск и мониторинг

* Запуск из CLI:

```bash
prefect deployment run "hello/hello" -p '{"name": "team"}'
```

* Мониторинг: UI → `http://192.168.1.35:4200` (Flows, Deployments, Runs, Logs).

---

## 5) Как мигрировать существующие скрипты/локальные Prefect-инстансы

1. Удалите всё, что стартует локальный сервер (`prefect server start`/Docker-compose локального сервера).
2. Вставьте `prefect config set PREFECT_API_URL=http://192.168.1.35:4200/api`.
3. Оберните ваш скрипт в `@flow`/`@task` (см. пример выше).
4. Выберите вариант деплоя:

   * **A (образ):** соберите образ с вашим кодом и задеплойте в `docker-pool`.
   * **B (Git):** подключите блок Git + дефолтный образ `prefecthq/prefect:3-latest`.
5. Запускайте через Deployment, а не «python script.py» — так появятся история запусков, ретраи, параметры, расписания.

---

## 6) Параметры, секреты, расписания

* Параметры указывайте в `deployment` и/или при запуске (`-p '{"k": "v"}'`).
* Секреты храните в **Blocks** (например, Credentials/Git/S3) и подключайте их в деплоях.
* Расписания добавляйте в `prefect.yaml` (раздел `schedules`) или через UI.

---

## 7) Для AI-агентов (программный триггер запусков)

Минимальный вызов деплоя из Python:

```python
import asyncio
from prefect.client.orchestration import get_client

async def trigger(deployment_id, params=None):
    async with get_client() as client:
        run = await client.create_flow_run_from_deployment(
            deployment_id=deployment_id,
            parameters=params or {}
        )
        return run.id

# asyncio.run(trigger(UUID("..."), {"name": "agent"}))
```

> Агенту достаточно иметь `PREFECT_API_URL` и знать `deployment_id` или имя деплоя.

---

## 8) Частые ошибки и быстрые проверки

* **UI пишет про 127.0.0.1:** жёстко обновите кэш (Ctrl+Shift+R), удалите service worker и убедитесь, что сервер отдаёт корректный `api_url`.
* **Пул не найден:** убедитесь, что деплой указывает `pool: docker-pool` (пул создан на сервере).
* **Код не найден в контейнере:** либо используйте образ с кодом (**A**), либо Git/S3 storage (**B**).

---

### Итог

* Единая точка входа для всех: `PREFECT_API_URL=http://192.168.1.35:4200/api`.
* Деплои всегда целятся в `docker-pool`.
* Для продакшена предпочтителен деплой **через Docker-образ**; для быстрых прототипов — **через Git-storage**.
