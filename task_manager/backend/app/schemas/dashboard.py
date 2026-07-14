"""Response schema for the dashboard endpoint."""

from pydantic import BaseModel

from app.schemas.task import TaskResponse


class DashboardStats(BaseModel):
    total: int
    pending: int
    in_progress: int
    review: int
    completed: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_tasks: list[TaskResponse]
