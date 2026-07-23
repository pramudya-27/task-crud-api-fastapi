from app.domain import Task
from app.errors import ApiError
from app.repositories.base import TaskRepository


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
    ) -> None:
        self.repository = repository

    def list_tasks(self) -> list[Task]:
        return self.repository.list_all()

    def get_task(self, task_id: int) -> Task:
        task = self.repository.get_by_id(task_id)

        if task is None:
            raise ApiError(
                status_code=404,
                message="Task not found",
            )

        return task

    def create_task(
        self,
        title: str | None,
    ) -> Task:
        if title is None or not title.strip():
            raise ApiError(
                status_code=400,
                message="Title is required and cannot be empty",
            )

        return self.repository.create(
            title=title.strip(),
        )

    def update_task(
        self,
        task_id: int,
        changes: dict[str, object],
    ) -> Task:
        if not changes:
            raise ApiError(
                status_code=400,
                message="Request body cannot be empty",
            )

        clean_changes: dict[str, object] = {}

        if "title" in changes:
            title = changes["title"]

            if not isinstance(title, str) or not title.strip():
                raise ApiError(
                    status_code=400,
                    message="Title cannot be empty",
                )

            clean_changes["title"] = title.strip()

        if "done" in changes:
            done = changes["done"]

            if not isinstance(done, bool):
                raise ApiError(
                    status_code=400,
                    message="Done must be true or false",
                )

            clean_changes["done"] = done

        updated_task = self.repository.update(
            task_id=task_id,
            changes=clean_changes,
        )

        if updated_task is None:
            raise ApiError(
                status_code=404,
                message="Task not found",
            )

        return updated_task

    def delete_task(self, task_id: int) -> None:
        deleted = self.repository.delete(task_id)

        if not deleted:
            raise ApiError(
                status_code=404,
                message="Task not found",
            )