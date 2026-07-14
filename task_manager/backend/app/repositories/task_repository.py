"""Database access for the `tasks` table. No business logic lives here."""

from uuid import UUID

from supabase import Client

from app.models.task import Task, TaskStatus

_TABLE = "tasks"


class TaskRepository:
    def __init__(self, client: Client) -> None:
        self._client = client

    def list(
        self, status: TaskStatus | None = None, assigned_to: UUID | None = None
    ) -> list[Task]:
        """List tasks, most recently created first, with optional filters."""
        query = self._client.table(_TABLE).select("*").order("created_at", desc=True)
        if status is not None:
            query = query.eq("status", status.value)
        if assigned_to is not None:
            query = query.eq("assigned_to", str(assigned_to))
        result = query.execute()
        return [Task.model_validate(row) for row in result.data]

    def get_by_id(self, task_id: UUID) -> Task | None:
        result = (
            self._client.table(_TABLE)
            .select("*")
            .eq("id", str(task_id))
            .maybe_single()
            .execute()
        )
        if result.data is None:
            return None
        return Task.model_validate(result.data)

    def create(self, data: dict) -> Task:
        result = self._client.table(_TABLE).insert(data).execute()
        return Task.model_validate(result.data[0])

    def update(self, task_id: UUID, data: dict) -> Task | None:
        result = self._client.table(_TABLE).update(data).eq("id", str(task_id)).execute()
        if not result.data:
            return None
        return Task.model_validate(result.data[0])

    def delete(self, task_id: UUID) -> bool:
        result = self._client.table(_TABLE).delete().eq("id", str(task_id)).execute()
        return bool(result.data)
