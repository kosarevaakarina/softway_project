from src.core.config import redis_settings

from .task_worker import process_task


class WorkerSettings:
    """Конфигурация arq-воркера: список фоновых задач и подключение к Redis."""
    functions = [process_task]
    redis_settings = redis_settings
