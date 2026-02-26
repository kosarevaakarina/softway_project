from src.application.task_service import TaskService
from src.infrastructure.postgres.database import new_session
from src.infrastructure.postgres.repository import PostgresTaskRepository


class _NoOpQueue:
    """Воркер не ставит задачи в очередь, поэтому заглушка."""
    async def enqueue(self, task_id: int) -> None:
        pass


async def process_task(ctx: dict, task_id: int) -> None:
    async with new_session() as session:
        repo = PostgresTaskRepository(session)
        service = TaskService(repo=repo, queue=_NoOpQueue())  # type: ignore[arg-type]
        await service.process_task(task_id)
