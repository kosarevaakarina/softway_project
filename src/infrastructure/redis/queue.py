from arq import ArqRedis

from src.domain.interfaces import TaskQueue


class ArqTaskQueue(TaskQueue):
    def __init__(self, redis: ArqRedis) -> None:
        self._redis = redis

    async def enqueue(self, task_id: int) -> None:
        await self._redis.enqueue_job("process_task", task_id)
