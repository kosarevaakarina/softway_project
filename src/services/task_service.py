from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import logger
from src.exceptions import TaskNotFoundException
from src.models.task import Task, TaskStatus
from src.repositories.postgres.task import TaskCrud
from src.schemas.task_schema import TaskCreate


class TaskService:
    @staticmethod
    async def create_task(
        task_data: TaskCreate,
        session: AsyncSession,
        redis: ArqRedis,
    ) -> Task:
        """Создание задачи и постановка её в очередь обработки."""
        task = await TaskCrud.create_task(task_data, session)
        await redis.enqueue_job("process_task", task.id)
        logger.info("Created task %s (title=%r), enqueued for processing", task.id, task.title)
        return task

    @staticmethod
    async def list_tasks(
        status: TaskStatus,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Task], int]:
        """Получение списка задач по статусу с пагинацией."""
        tasks = await TaskCrud.get_tasks(session, status, offset, limit)
        total = await TaskCrud.count_tasks(session, status)
        logger.info("Listed tasks: status=%s, total=%s, offset=%s, limit=%s", status, total, offset, limit)
        return tasks, total

    @staticmethod
    async def get_task(
        task_id: int,
        session: AsyncSession,
    ) -> Task:
        """Получение задачи по идентификатору или ошибка 404."""
        task = await TaskCrud.get_task(task_id, session)
        if task is None:
            raise TaskNotFoundException(task_id)
        return task
