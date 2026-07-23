from fastapi import APIRouter, Depends, Response

from app.dependencies import get_task_service
from app.schemas import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import TaskService


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.get(
    "",
    response_model=list[TaskResponse],
    summary="List all tasks",
)
def list_tasks(
    service: TaskService = Depends(get_task_service),
):
    return service.list_tasks()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    return service.get_task(task_id)


@router.post(
    "",
    status_code=201,
    response_model=TaskResponse,
    summary="Create a task",
)
def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    return service.create_task(payload.title)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    changes = payload.model_dump(
        exclude_unset=True
    )

    return service.update_task(
        task_id=task_id,
        changes=changes,
    )


@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Delete a task",
)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    service.delete_task(task_id)

    return Response(status_code=204)