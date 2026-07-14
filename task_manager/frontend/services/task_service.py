"""API client calls for task CRUD and status changes."""

from services.api_client import ApiClient

_client = ApiClient()


def list_tasks(status: str | None = None, assigned_to: str | None = None) -> list[dict]:
    params = {}
    if status:
        params["status"] = status
    if assigned_to:
        params["assigned_to"] = assigned_to
    return _client.get("/tasks", params=params)


def create_task(payload: dict) -> dict:
    return _client.post("/tasks", json=payload)


def update_task(task_id: str, payload: dict) -> dict:
    return _client.put(f"/tasks/{task_id}", json=payload)


def delete_task(task_id: str) -> None:
    _client.delete(f"/tasks/{task_id}")


def update_status(task_id: str, status: str) -> dict:
    return _client.patch(f"/tasks/{task_id}/status", json={"status": status})
