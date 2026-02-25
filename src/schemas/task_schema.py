from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)


class TaskInfo(BaseModel):
    id: int
    title: str
    status: TaskStatus
    result: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    items: list[TaskInfo]
    total: int
    offset: int
    limit: int
