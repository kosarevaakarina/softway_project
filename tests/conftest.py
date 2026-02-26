import asyncio
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.domain.entities import Task, TaskStatus


def make_task(
    id: int = 1,
    title: str = "Test task",
    status: TaskStatus = TaskStatus.new,
    result: str | None = None,
) -> Task:
    return Task(
        id=id,
        title=title,
        status=status,
        result=result,
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        updated_at=datetime(2026, 1, 1, 12, 0, 0),
    )


def run_async(coro):
    return asyncio.run(coro)


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_id_for_update = AsyncMock()
    repo.list_by_status = AsyncMock()
    repo.count_by_status = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_queue():
    queue = AsyncMock()
    queue.enqueue = AsyncMock()
    return queue
