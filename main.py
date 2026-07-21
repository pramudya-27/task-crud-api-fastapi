import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import (
    BaseModel,
    ConfigDict,
    StrictBool,
    StrictStr,
)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE_PATH = Path(__file__).parent / "tasks.db"


def get_database_connection():
    """
    Opens a new SQLite connection.

    A new connection is created for each operation and
    closed automatically after leaving the with block.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Creates the database schema and seeds the table.

    Example tasks are inserted only when the tasks table
    contains no rows.
    """

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
            """
            SELECT COUNT(*) AS total
            FROM tasks
            """
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
    Converts an SQLite row into a JSON-compatible dictionary.
    """

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def find_task_row(connection, task_id: int):
    """
    Finds one task from SQLite based on its ID.
    """

    return connection.execute(
        """
        SELECT id, title, done
        FROM tasks
        WHERE id = ?
        """,
        (task_id,),
    ).fetchone()


# =========================================================
# REQUEST MODELS
# =========================================================

class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: StrictStr | None = None


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: StrictStr | None = None
    done: StrictBool | None = None


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
        "A CRUD API for managing to-do tasks using SQLite. "
        "The API endpoints remain the same as the in-memory "
        "version, but the data now survives server restarts."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
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
    """
    Converts FastAPI's default validation response into
    400 Bad Request as required by the assignment.
    """

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
    description="Returns basic information about the Task API.",
    response_description="API information",
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
    description="Checks whether the API server is running.",
    response_description="Server health status",
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
    description="Returns all tasks stored in the SQLite database.",
    response_description="A list containing all tasks",
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
    description=(
        "Returns one task from SQLite based on its ID. "
        "An unknown ID returns 404 Not Found."
    ),
    response_description="The requested task",
    responses={
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Task not found",
                    }
                }
            },
        }
    },
    tags=["Tasks"],
)
def get_task(task_id: int):
    with get_database_connection() as connection:
        row = find_task_row(connection, task_id)

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
    description=(
        "Inserts a new task into SQLite. "
        "The server sets done to false automatically."
    ),
    response_description="The newly created task",
    responses={
        201: {
            "description": "Task successfully created",
        },
        400: {
            "description": "Invalid request body",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Title is required and cannot be empty",
                    }
                }
            },
        },
    },
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

        row = find_task_row(
            connection,
            new_task_id,
        )

    return convert_task_row(row)


# =========================================================
# UPDATE TASK
# =========================================================

@app.put(
    "/tasks/{task_id}",
    summary="Update an existing task",
    description=(
        "Updates the title, done status, or both fields "
        "of an existing task using an SQL UPDATE query."
    ),
    response_description="The updated task",
    responses={
        400: {
            "description": "Invalid or empty request body",
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Task not found",
                    }
                }
            },
        },
    },
    tags=["Tasks"],
)
def update_task(task_id: int, payload: TaskUpdate):
    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Request body cannot be empty",
            },
        )

    update_columns = []
    update_values = []

    if "title" in changes:
        title = changes["title"]

        if title is None or not title.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Title cannot be empty",
                },
            )

        update_columns.append("title = ?")
        update_values.append(title.strip())

    if "done" in changes:
        done = changes["done"]

        if done is None:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Done must be true or false",
                },
            )

        update_columns.append("done = ?")
        update_values.append(int(done))

    with get_database_connection() as connection:
        existing_task = find_task_row(
            connection,
            task_id,
        )

        if existing_task is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Task not found",
                },
            )

        update_values.append(task_id)

        sql_query = (
            "UPDATE tasks SET "
            + ", ".join(update_columns)
            + " WHERE id = ?"
        )

        connection.execute(
            sql_query,
            update_values,
        )

        connection.commit()

        updated_row = find_task_row(
            connection,
            task_id,
        )

    return convert_task_row(updated_row)


# =========================================================
# DELETE TASK
# =========================================================

@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete an existing task",
    description=(
        "Deletes a task from SQLite using an SQL DELETE query. "
        "A successful deletion returns 204 No Content."
    ),
    responses={
        204: {
            "description": "Task successfully deleted",
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Task not found",
                    }
                }
            },
        },
    },
    tags=["Tasks"],
)
def delete_task(task_id: int):
    with get_database_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        if cursor.rowcount == 0:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Task not found",
                },
            )

        connection.commit()

    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)