from fastapi import HTTPException
from starlette import status

from src.core.logger import logger


class TaskNotFoundException(HTTPException):
    def __init__(self, task_id: int):
        logger.error("Not found: Task ID=%s does not exist", task_id)
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found: Task does not exist",
        )
