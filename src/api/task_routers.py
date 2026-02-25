from arq import ArqRedis
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.core.redis import get_redis
from src.models.task import TaskStatus
from src.schemas.task_schema import TaskCreate, TaskInfo, TaskListResponse
from src.services.task_service import TaskService

router = APIRouter()


@router.post("/", response_model=TaskInfo, status_code=201)
async def create_task(
    task_data: TaskCreate = Body(...),
    session: AsyncSession = Depends(get_session),
    redis: ArqRedis = Depends(get_redis),
):
    """Создание задачи."""
    task = await TaskService.create_task(task_data, session, redis)
    return TaskInfo.model_validate(task)


@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    status: TaskStatus,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Просмотр задач с фильтрацией по статусу и пагинацией."""
    tasks, total = await TaskService.list_tasks(status, session, offset, limit)
    return TaskListResponse(
        items=[TaskInfo.model_validate(task) for task in tasks],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{task_id}/", response_model=TaskInfo)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Получение одной задачи."""
    task = await TaskService.get_task(task_id, session)
    return TaskInfo.model_validate(task)
