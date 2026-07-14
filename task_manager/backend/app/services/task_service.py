"""Business logic for task CRUD and status changes."""

from uuid import UUID

from app.models.task import Task, TaskStatus
from app.repositories.profile_repository import ProfileRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.utils.exceptions import NotFoundError, ValidationError


class TaskService:
    def __init__(self, task_repo: TaskRepository, profile_repo: ProfileRepository) -> None:
        self._task_repo = task_repo
        self._profile_repo = profile_repo

    def list_tasks(
        self, status: TaskStatus | None = None, assigned_to: UUID | None = None
    ) -> list[Task]:
        return self._task_repo.list(status=status, assigned_to=assigned_to)

    def create_task(self, data: TaskCreate) -> Task:
        self._ensure_assignee_exists(data.assigned_to)
        payload = {
            "title": data.title,
            "description": data.description,
            "priority": data.priority.value,
            "status": data.status.value,
            "assigned_to": str(data.assigned_to),
        }
        return self._task_repo.create(payload)

    def update_task(self, task_id: UUID, data: TaskUpdate) -> Task:
        self._ensure_assignee_exists(data.assigned_to)
        payload = {
            "title": data.title,
            "description": data.description,
            "priority": data.priority.value,
            "status": data.status.value,
            "assigned_to": str(data.assigned_to),
        }
        updated = self._task_repo.update(task_id, payload)
        if updated is None:
            raise NotFoundError(f"Task {task_id} not found")
        return updated

    def delete_task(self, task_id: UUID) -> None:
        if not self._task_repo.delete(task_id):
            raise NotFoundError(f"Task {task_id} not found")

    def update_status(self, task_id: UUID, status: TaskStatus) -> Task:
        updated = self._task_repo.update(task_id, {"status": status.value})
        if updated is None:
            raise NotFoundError(f"Task {task_id} not found")
        return updated

    def _ensure_assignee_exists(self, profile_id: UUID) -> None:
        if self._profile_repo.get_by_id(profile_id) is None:
            raise ValidationError(f"assigned_to references a nonexistent user: {profile_id}")
