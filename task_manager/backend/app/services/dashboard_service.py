"""Business logic for aggregating dashboard statistics."""

from app.models.task import TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.dashboard import DashboardResponse, DashboardStats

_RECENT_TASKS_LIMIT = 5


class DashboardService:
    def __init__(self, task_repo: TaskRepository) -> None:
        self._task_repo = task_repo

    def get_dashboard(self) -> DashboardResponse:
        """Fetch all tasks once and derive both stats and the recent list from it."""
        tasks = self._task_repo.list()

        stats = DashboardStats(
            total=len(tasks),
            pending=sum(1 for t in tasks if t.status == TaskStatus.PENDING),
            in_progress=sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS),
            review=sum(1 for t in tasks if t.status == TaskStatus.REVIEW),
            completed=sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
        )
        recent_tasks = tasks[:_RECENT_TASKS_LIMIT]

        return DashboardResponse(stats=stats, recent_tasks=recent_tasks)
