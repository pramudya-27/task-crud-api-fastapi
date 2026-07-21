import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE_PATH = Path(__file__).parent / "tasks.db"


def get_database_connection():
    """
    Creates and returns a connection to the SQLite database.

    row_factory makes query results accessible using
    column names, such as row["title"].
    """

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Creates the tasks table when it does not exist.

    Three example tasks are inserted only when the table
    is completely empty.
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


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes the database when the application starts.
    """

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)