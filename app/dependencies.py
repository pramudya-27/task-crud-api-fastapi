import os

from dotenv import load_dotenv

from app.repositories.postgres import PostgresTaskRepository
from app.services.task_service import TaskService


load_dotenv()


database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not configured"
    )


repository = PostgresTaskRepository(
    database_url=database_url,
)

task_service = TaskService(
    repository=repository,
)


def get_task_service() -> TaskService:
    return task_service