import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.task import Task, TaskStatus


def make_task(
    id: int = 1,
    title: str = "Test task",
    status: TaskStatus = TaskStatus.new,
    result: str | None = None,
) -> MagicMock:
    """Создаёт мок ORM-объекта Task."""
    task = MagicMock(spec=Task)
    task.id = id
    task.title = title
    task.status = status
    task.result = result
    task.created_at = datetime(2026, 1, 1, 12, 0, 0)
    task.updated_at = datetime(2026, 1, 1, 12, 0, 0)
    return task


def run_async(coro):
    """Запускает корутину синхронно."""
    return asyncio.run(coro)


@pytest.fixture
def mock_session():
    """Мок AsyncSession — имитация БД."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_redis():
    """Мок Redis — имитация очереди задач."""
    redis = AsyncMock()
    redis.enqueue_job = AsyncMock(return_value=None)
    return redis
