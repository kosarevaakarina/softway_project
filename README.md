# Task Processing Service

Мини-сервис управления задачами с асинхронной обработкой.

**Стек:** Python 3.13, FastAPI, PostgreSQL, Redis, ARQ, SQLAlchemy, Alembic, Docker.

## Запуск

### Docker 

```bash
# Запуск из корня проекта
docker compose -f docker/docker-compose.yaml up --build
```

Сервис будет доступен по адресу: http://localhost:8000

Swagger-документация: http://localhost:8000/docs

### Локально

```bash
# Установить зависимости
poetry install

# Применить миграции
poetry run alembic -c src/alembic.ini upgrade head

# Запустить приложение
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# В отдельном терминале — запустить воркер 
poetry run arq src.workers.config.WorkerSettings
```

### Тесты

```bash
poetry install --with dev
poetry run pytest -v
```

## API

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/tasks/` | Создание задачи (тело: `{"title": "..."}`) |
| GET | `/tasks/?status=new&offset=0&limit=10` | Список задач с фильтрацией и пагинацией |
| GET | `/tasks/{id}/` | Получение одной задачи |

## Архитектура

Проект построен по слоистой архитектуре с чётким разделением ответственности между слоями:

- **API-слой** (`src/api/`) — FastAPI-роутеры. Принимает HTTP-запросы, валидирует входные данные через Pydantic-схемы и делегирует обработку сервисному слою.
- **Сервисный слой** (`src/services/`) — координирует бизнес-логику: создание задачи с постановкой в очередь, получение задач с пагинацией, обработка ошибок.
- **Репозиторий** (`src/repositories/`) — инкапсулирует все запросы к PostgreSQL через SQLAlchemy.
- **Воркер** (`src/workers/`) — ARQ-воркер, работающий как отдельный процесс. Забирает задачи из Redis-очереди, меняет статус задач.
- **Core** (`src/core/`) — общая инфраструктура.

Миграции БД управляются через Alembic (`src/migrations/`).

## Что бы улучшили в production

- **Аутентификация и авторизация** 
- **Retry-логика в воркере** 
- **Мониторинг и алерты**
- **CI/CD**
- **Healthcheck-эндпоинт**
