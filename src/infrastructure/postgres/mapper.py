from src.domain.entities import Task, TaskStatus

from .models import TaskModel


class TaskMapper:
    @staticmethod
    def to_entity(model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            status=TaskStatus(model.status),
            result=model.result,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Task) -> TaskModel:
        return TaskModel(
            id=entity.id,
            title=entity.title,
            status=entity.status,
            result=entity.result,
        )
