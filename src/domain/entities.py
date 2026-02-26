import enum
from dataclasses import dataclass, field
from datetime import datetime


class TaskStatus(str, enum.Enum):
    new = "new"
    processing = "processing"
    done = "done"
    failed = "failed"


@dataclass
class Task:
    id: int
    title: str
    status: TaskStatus = TaskStatus.new
    result: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
