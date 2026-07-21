import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse


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
    """
    Converts an SQLite row into the API response format.

    SQLite stores boolean values as 0 and 1. The API
    returns them as false and true.
    """

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)