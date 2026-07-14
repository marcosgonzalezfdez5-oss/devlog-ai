"""Domain enums and internal representation of a task."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    COMPLETED = "Completed"


class Task(BaseModel):
    """Internal representation of a `tasks` row, as returned by the repository."""

    id: UUID
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    assigned_to: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
