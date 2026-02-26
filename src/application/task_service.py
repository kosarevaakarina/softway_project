from src.core.logger import logger
from src.domain.entities import Task, TaskStatus
from src.domain.exceptions import TaskNotFoundError
from src.domain.interfaces import TaskQueue, TaskRepository


class TaskService:
    def __init__(self, repo: TaskRepository, queue: TaskQueue) -> None:
        self._repo = repo
        self._queue = queue

    async def create_task(self, title: str) -> Task:
        task = await self._repo.create(title)
        await self._queue.enqueue(task.id)
        logger.info("Created task %s (title=%r), enqueued", task.id, task.title)
        return task

    async def list_tasks(
        self,
        status: TaskStatus,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Task], int]:
        tasks = await self._repo.list_by_status(status, offset, limit)
        total = await self._repo.count_by_status(status)
        logger.info("Listed tasks: status=%s, total=%s", status, total)
        return tasks, total

    async def get_task(self, task_id: int) -> Task:
        task = await self._repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    async def process_task(self, task_id: int) -> None:
        """Фоновая обработка: processing -> done/failed."""
        task = await self._repo.get_by_id_for_update(task_id)

        if task is None:
            logger.warning("Task %s not found, skipping", task_id)
            return

        if task.status != TaskStatus.new:
            logger.warning("Task %s status '%s', expected 'new' — skipping", task_id, task.status)
            return

        try:
            task.status = TaskStatus.processing
            await self._repo.save(task)
            logger.info("Task %s status -> processing", task_id)

            import asyncio
            await asyncio.sleep(3)

            if len(task.title) % 2 == 0:
                task.status = TaskStatus.done
                task.result = "success"
            else:
                task.status = TaskStatus.failed
                task.result = "error"

            await self._repo.save(task)
            logger.info("Task %s finished: status=%s, result=%s", task_id, task.status, task.result)

        except Exception:
            logger.exception("Task %s failed with unexpected error", task_id)
            task.status = TaskStatus.failed
            task.result = "internal error"
            await self._repo.save(task)
