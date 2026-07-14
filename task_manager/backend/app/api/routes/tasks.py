"""Task CRUD and status-change endpoints. All routes require authentication."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_task_service
from app.models.task import TaskStatus
from app.schemas.error import ErrorResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskStatusUpdate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/tasks", tags=["tasks"], dependencies=[Depends(get_current_user)]
)

_common_responses = {
    401: {"model": ErrorResponse, "description": "Missing or invalid token"},
    404: {"model": ErrorResponse, "description": "Task not found"},
}


@router.get(
    "",
    response_model=list[TaskResponse],
    summary="List tasks",
    description="Returns tasks ordered by most recently created, optionally filtered by status and/or assignee.",
)
def list_tasks(
    status: TaskStatus | None = None,
    assigned_to: UUID | None = None,
    task_service: TaskService = Depends(get_task_service),
) -> list[TaskResponse]:
    return task_service.list_tasks(status=status, assigned_to=assigned_to)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=201,
    responses={422: {"model": ErrorResponse, "description": "assigned_to references a nonexistent user"}},
    summary="Create a task",
)
def create_task(
    payload: TaskCreate, task_service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    return task_service.create_task(payload)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses=_common_responses,
    summary="Replace a task",
)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return task_service.update_task(task_id, payload)


@router.delete(
    "/{task_id}",
    status_code=204,
    responses=_common_responses,
    summary="Delete a task",
)
def delete_task(
    task_id: UUID, task_service: TaskService = Depends(get_task_service)
) -> None:
    task_service.delete_task(task_id)


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    responses=_common_responses,
    summary="Change a task's status",
)
def update_task_status(
    task_id: UUID,
    payload: TaskStatusUpdate,
    task_service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return task_service.update_status(task_id, payload.status)
