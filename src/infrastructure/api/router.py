from fastapi import APIRouter, Body, Depends, Query
from starlette import status
from starlette.responses import JSONResponse

from src.domain.entities import TaskStatus
from src.domain.exceptions import TaskNotFoundError

from .dependencies import get_task_service
from .schemas import TaskCreateRequest, TaskListResponse, TaskResponse

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    body: TaskCreateRequest = Body(...),
    service=Depends(get_task_service),
):
    task = await service.create_task(body.title)
    return TaskResponse.model_validate(task)


@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    status_filter: TaskStatus = Query(..., alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service=Depends(get_task_service),
):
    tasks, total = await service.list_tasks(status_filter, offset, limit)
    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{task_id}/", response_model=TaskResponse)
async def get_task(
    task_id: int,
    service=Depends(get_task_service),
):
    try:
        task = await service.get_task(task_id)
    except TaskNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Task not found"},
        )
    return TaskResponse.model_validate(task)
