from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient 
from unittest.mock import Mock
from datetime import datetime, timezone

from app.dependencies import get_current_user, get_task_service
from app.main import app
from app.models.auth import AuthenticatedUser
from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskStatusUpdate,TaskUpdate


def make_task(task_id : UUID, assigned_to: UUID) -> Task:
    now = datetime.now(timezone.utc)
    return Task(
        id = task_id,
        title = "Integration Task",
        description = "Task via API",
        priority = TaskPriority.HIGH,
        status = TaskStatus.PENDING,
        assigned_to = assigned_to,
        created_at = now,
        updated_at = now
    )

@pytest.fixture(autouse=True)
def fake_auth_override():
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id = str(uuid4()),email = "test@example.com")
    yield
    app.dependency_overrides.pop(get_current_user,None)

def test_list_task_route_returns_tasks():
    task_id = uuid4()
    assigned_id = uuid4()
    task = make_task(task_id,assigned_id)

    task_service = Mock()
    task_service.list_tasks.return_value = [task]

    app.dependency_overrides[get_task_service] = lambda: task_service

    client = TestClient(app)
    response = client.get("/tasks")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,list)
    assert data[0]["id"] == str(task_id)
    assert data[0]["title"] == "Integration Task"

    app.dependency_overrides.pop(get_task_service,None)


def test_update_task_route_return_task():
    task_id = uuid4()
    assigned_id = uuid4()
    updated_task = make_task(task_id,assigned_id)
    updated_task.title = "Integration Task Updated"
    updated_task.status = TaskStatus.IN_PROGRESS

    task_service = Mock()
    task_service.update_task.return_value = updated_task

    app.dependency_overrides[get_task_service] = lambda:task_service 

    client = TestClient(app)
    response = client.put(f"/tasks/{task_id}",
                          json = {
                              "title": "Integration Task Updated",
                              "description": "Updated via API",
                              "priority": TaskPriority.HIGH.value,
                              "status": TaskStatus.IN_PROGRESS.value,
                              "assigned_to": str(assigned_id)
                          })
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(task_id)
    assert body["title"] == "Integration Task Updated"
    assert body["status"] == TaskStatus.IN_PROGRESS.value

    task_service.update_task.assert_called_once_with(
        task_id,
        TaskUpdate(
            title="Integration Task Updated",
            description="Updated via API",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            assigned_to=assigned_id
        )
        
    )

    app.dependency_overrides.pop(get_task_service,None)


def test_delete_task_route_returns_no_content():
    task_id = uuid4()

    task_service = Mock()
    task_service.delete_task.return_value = None

    app.dependency_overrides[get_task_service] = lambda: task_service

    client = TestClient(app)
    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    task_service.delete_task.assert_called_once_with(task_id)

    app.dependency_overrides.pop(get_task_service, None)

