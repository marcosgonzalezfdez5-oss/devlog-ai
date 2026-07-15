from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import UUID,uuid4
import pytest
from app.models.task import Task, TaskPriority, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService
from app.utils.exceptions import NotFoundError, ValidationError  



def make_task(task_id:UUID, assigned_to: UUID) -> Task:
    now = datetime.now(timezone.utc)
    return Task(
        id = task_id,
        title = "Test Task",
        description = "This is a test task.",
        priority = TaskPriority.MEDIUM,
        status = TaskStatus.PENDING,
        assigned_to = assigned_to,
        created_at = now,
        updated_at = now, 
    )

def test_create_task():
    task_id = uuid4()
    assigned_id = uuid4()

    task_repo = Mock(spec=TaskRepository)
    profile_repo = Mock(spec=ProfileRepository)

    profile_repo.get_by_id.return_value =  {"id": str(assigned_id)}
    task_repo.create.return_value = make_task(task_id, assigned_id)

    service = TaskService(task_repo, profile_repo)

    payload = TaskCreate(
        title="Test Task",
        description="This is a test task.",
        priority=TaskPriority.MEDIUM,
        assigned_to=assigned_id,
    )

    result = service.create_task(payload)

    profile_repo.get_by_id.assert_called_once_with(assigned_id)
    task_repo.create.assert_called_once()

    assert result.id == task_id
    assert result.priority == TaskPriority.MEDIUM
    assert result.assigned_to == assigned_id



def test_create_task_raises_when_assignee_missing():
    assignee_id = uuid4()

    task_repo = Mock(spec=TaskRepository)
    profile_repo = Mock(spec=ProfileRepository)
    profile_repo.get_by_id.return_value = None

    service = TaskService(task_repo, profile_repo)
    payload = TaskCreate(
        title="New task",
        description="Create a task",
        priority=TaskPriority.LOW,
        assigned_to=assignee_id,
    )

    with pytest.raises(ValidationError):
        service.create_task(payload)

def test_update_task():
    task_id = uuid4()
    assigned_id = uuid4()

    task_repo = Mock(spec=TaskRepository)
    profile_repo = Mock(spec=ProfileRepository)

    profile_repo.get_by_id.return_value = {"id": str(assigned_id)}
    updated_task = make_task(task_id, assigned_id)
    updated_task.title = "Updated Task"
    updated_task.status = TaskStatus.IN_PROGRESS
    task_repo.update.return_value = updated_task

    service = TaskService(task_repo, profile_repo)

    payload = TaskUpdate(
        title="Updated Task",
        description="This task has been updated.",
        priority=TaskPriority.HIGH,
        status=TaskStatus.IN_PROGRESS,
        assigned_to=assigned_id,
    )

    result = service.update_task(task_id, payload)

    profile_repo.get_by_id.assert_called_once_with(assigned_id)
    task_repo.update.assert_called_once_with(
        task_id,
        {
            "title": "Updated Task",
            "description": "This task has been updated.",
            "priority": TaskPriority.HIGH.value,
            "status": TaskStatus.IN_PROGRESS.value,
            "assigned_to": str(assigned_id),
        },
    )
    assert result.title == "Updated Task"
    assert result.status == TaskStatus.IN_PROGRESS


def test_delete_task():
    task_id = uuid4()

    task_repo = Mock(spec=TaskRepository)
    profile_repo = Mock(spec=ProfileRepository)

    task_repo.delete.return_value = True

    service = TaskService(task_repo, profile_repo)
    service.delete_task(task_id)

    task_repo.delete.assert_called_once_with(task_id)

