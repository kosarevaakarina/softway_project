from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Task, TaskStatus
from src.domain.interfaces import TaskRepository

from .models import TaskModel


class PostgresTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, title: str) -> Task:
        row = TaskModel(title=title)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return row.to_entity()

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        row = result.scalars().first()
        return row.to_entity() if row else None

    async def get_by_id_for_update(self, task_id: int) -> Task | None:
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.id == task_id).with_for_update()
        )
        row = result.scalars().first()
        return row.to_entity() if row else None

    async def list_by_status(self, status: TaskStatus, offset: int, limit: int) -> list[Task]:
        query = (
            select(TaskModel)
            .where(TaskModel.status == status)
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [row.to_entity() for row in result.scalars().all()]

    async def count_by_status(self, status: TaskStatus) -> int:
        query = select(func.count()).select_from(TaskModel).where(TaskModel.status == status)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def save(self, task: Task) -> None:
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.id == task.id)
        )
        row = result.scalars().first()
        if row is None:
            return
        row.status = task.status  # type: ignore[assignment]
        row.result = task.result  # type: ignore[assignment]
        await self._session.commit()
