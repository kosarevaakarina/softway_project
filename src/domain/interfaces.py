from abc import ABC, abstractmethod

from src.domain.entities import Task, TaskStatus


class TaskRepository(ABC):
    @abstractmethod
    async def create(self, title: str) -> Task: ...

    @abstractmethod
    async def get_by_id(self, task_id: int) -> Task | None: ...

    @abstractmethod
    async def get_by_id_for_update(self, task_id: int) -> Task | None: ...

    @abstractmethod
    async def list_by_status(self, status: TaskStatus, offset: int, limit: int) -> list[Task]: ...

    @abstractmethod
    async def count_by_status(self, status: TaskStatus) -> int: ...

    @abstractmethod
    async def save(self, task: Task) -> None: ...


class TaskQueue(ABC):
    @abstractmethod
    async def enqueue(self, task_id: int) -> None: ...
