from app.repositories.sqlite import SQLiteTaskRepository
from app.services.task_service import TaskService


repository = SQLiteTaskRepository(
    database_path="tasks.db",
)

task_service = TaskService(
    repository=repository,
)


def get_task_service() -> TaskService:
    return task_service