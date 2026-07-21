import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StrictStr


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE_PATH = Path(__file__).parent / "tasks.db"


def get_database_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    with get_database_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
                    CHECK (done IN (0, 1))
            )
            """
        )

        result = connection.execute(
            "SELECT COUNT(*) AS total FROM tasks"
        ).fetchone()

        if result["total"] == 0:
            example_tasks = [
                ("Learn FastAPI", 0),
                ("Connect CRUD API to SQLite", 0),
                ("Publish database project to GitHub", 1),
            ]

            connection.executemany(
                """
                INSERT INTO tasks (title, done)
                VALUES (?, ?)
                """,
                example_tasks,
            )

        connection.commit()


def convert_task_row(row: sqlite3.Row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


# =========================================================
# REQUEST MODEL
# =========================================================

class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: StrictStr | None = None


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Task API",
    version="2.0",
    description=(
        "A CRUD API for managing tasks using "
        "a persistent SQLite database."
    ),
    lifespan=lifespan,
)


# =========================================================
# VALIDATION ERROR HANDLER
# =========================================================

@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exception: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request body",
        },
    )


# =========================================================
# GENERAL ENDPOINTS
# =========================================================

@app.get(
    "/",
    summary="Get API information",
    tags=["General"],
)
def get_api_information():
    return {
        "name": "Task API",
        "version": "2.0",
        "database": "SQLite",
        "endpoints": ["/tasks"],
    }


@app.get(
    "/health",
    summary="Check server health",
    tags=["General"],
)
def health_check():
    return {
        "status": "ok",
    }


# =========================================================
# READ ALL TASKS
# =========================================================

@app.get(
    "/tasks",
    summary="List all tasks",
    description="Returns all tasks stored in SQLite.",
    tags=["Tasks"],
)
def get_all_tasks():
    with get_database_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, done
            FROM tasks
            ORDER BY id ASC
            """
        ).fetchall()

    return [
        convert_task_row(row)
        for row in rows
    ]


# =========================================================
# READ ONE TASK
# =========================================================

@app.get(
    "/tasks/{task_id}",
    summary="Get a task by ID",
    description="Returns one task from SQLite.",
    tags=["Tasks"],
)
def get_task(task_id: int):
    with get_database_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Task not found",
            },
        )

    return convert_task_row(row)


# =========================================================
# CREATE TASK
# =========================================================

@app.post(
    "/tasks",
    status_code=201,
    summary="Create a new task",
    description="Inserts a new task into SQLite.",
    tags=["Tasks"],
)
def create_task(payload: TaskCreate):
    if payload.title is None or not payload.title.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "Title is required and cannot be empty",
            },
        )

    clean_title = payload.title.strip()

    with get_database_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, done)
            VALUES (?, 0)
            """,
            (clean_title,),
        )

        new_task_id = cursor.lastrowid
        connection.commit()

        row = connection.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = ?
            """,
            (new_task_id,),
        ).fetchone()

    return convert_task_row(row)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)