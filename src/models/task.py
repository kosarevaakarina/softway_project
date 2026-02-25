import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, func

from src.core.db import Base


class TaskStatus(str, enum.Enum):
    """Статус задачи."""

    new = "new"
    processing = "processing"
    done = "done"
    failed = "failed"


class Task(Base):
    """Модель задачи."""

    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.new, index=True)
    result = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), onupdate=func.now())
