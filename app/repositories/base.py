from typing import Protocol

from app.domain import Task


class TaskRepository(Protocol):
    def list_all(self) -> list[Task]:
        """Return every task."""
        ...

    def get_by_id(self, task_id: int) -> Task | None:
        """Return one task or None."""
        ...

    def create(self, title: str) -> Task:
        """Create and return a task."""
        ...

    def update(
        self,
        task_id: int,
        changes: dict[str, object],
    ) -> Task | None:
        """Update a task or return None."""
        ...

    def delete(self, task_id: int) -> bool:
        """Delete a task and return its result."""
        ...