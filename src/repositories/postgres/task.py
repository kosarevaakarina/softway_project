from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task, TaskStatus
from src.schemas.task_schema import TaskCreate


class TaskCrud:
    @staticmethod
    async def create_task(task_data: TaskCreate, session: AsyncSession) -> Task:
        """Создание записи о задаче в БД."""
        new_task = Task(title=task_data.title)
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        return new_task

    @staticmethod
    async def get_tasks(
        session: AsyncSession,
        status: TaskStatus,
        offset: int = 0,
        limit: int = 10,
    ) -> list[Task]:
        """Получение задач по статусу с пагинацией."""
        query = select(Task).where(Task.status == status).offset(offset).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count_tasks(session: AsyncSession, status: TaskStatus) -> int:
        """Подсчёт общего количества задач с фильтрацией по статусу."""
        query = select(func.count()).select_from(Task).where(Task.status == status)
        result = await session.execute(query)
        return result.scalar_one()

    @staticmethod
    async def get_task(task_id: int, session: AsyncSession) -> Task | None:
        """Получение конкретной задачи по идентификатору."""
        result = await session.execute(select(Task).where(Task.id == task_id))
        return result.scalars().first()

    @staticmethod
    async def get_task_for_update(task_id: int, session: AsyncSession) -> Task | None:
        """Получение задачи с блокировкой строки (SELECT ... FOR UPDATE)."""
        result = await session.execute(
            select(Task).where(Task.id == task_id).with_for_update()
        )
        return result.scalars().first()
