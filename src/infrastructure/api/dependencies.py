from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.task_service import TaskService
from src.infrastructure.postgres.database import get_session
from src.infrastructure.postgres.repository import PostgresTaskRepository
from src.infrastructure.redis.queue import ArqTaskQueue


def _get_redis(request: Request):
    return request.app.state.redis


async def get_task_service(
    session: AsyncSession = Depends(get_session),
    redis=Depends(_get_redis),
) -> TaskService:
    repo = PostgresTaskRepository(session)
    queue = ArqTaskQueue(redis)
    return TaskService(repo=repo, queue=queue)
