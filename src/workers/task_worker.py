import asyncio

from src.core.db import new_session
from src.core.logger import logger
from src.models.task import TaskStatus
from src.repositories.postgres.task import TaskCrud


async def process_task(ctx: dict, task_id: int) -> None:
    """Фоновая обработка задачи."""
    logger.info("Processing task %s", task_id)

    async with new_session() as session:
        task = await TaskCrud.get_task_for_update(task_id, session)

        if task is None:
            logger.warning("Task %s not found, skipping", task_id)
            return

        if task.status != TaskStatus.new:
            logger.warning(
                "Task %s has status '%s', expected 'new' — skipping",
                task_id, task.status,
            )
            return

        try:
            task.status = TaskStatus.processing
            await session.commit()
            logger.info("Task %s status → processing", task_id)

            await asyncio.sleep(3)

            if len(task.title) % 2 == 0:
                task.status = TaskStatus.done
                task.result = "success"
            else:
                task.status = TaskStatus.failed
                task.result = "error"

            await session.commit()
            logger.info("Task %s finished: status=%s, result=%s", task_id, task.status, task.result)

        except Exception:
            logger.exception("Task %s failed with unexpected error", task_id)
            task.status = TaskStatus.failed
            task.result = "internal error"
            await session.commit()
