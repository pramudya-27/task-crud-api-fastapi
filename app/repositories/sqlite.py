import sqlite3
from pathlib import Path

from app.domain import Task


class SQLiteTaskRepository:
    def __init__(
        self,
        database_path: str = "tasks.db",
    ) -> None:
        self.database_path = (
            Path(__file__).resolve().parents[2]
            / database_path
        )

        self.initialize_database()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def initialize_database(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0
                )
                """
            )

            total = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM tasks
                """
            ).fetchone()["total"]

            if total == 0:
                connection.executemany(
                    """
                    INSERT INTO tasks (title, done)
                    VALUES (?, ?)
                    """,
                    [
                        ("Learn FastAPI", 0),
                        ("Connect CRUD to SQLite", 0),
                        ("Containerize the stack", 1),
                    ],
                )

            connection.commit()

    @staticmethod
    def to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            done=bool(row["done"]),
        )

    def list_all(self) -> list[Task]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, title, done
                FROM tasks
                ORDER BY id ASC
                """
            ).fetchall()

        return [
            self.to_task(row)
            for row in rows
        ]

    def get_by_id(
        self,
        task_id: int,
    ) -> Task | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT id, title, done
                FROM tasks
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()

        if row is None:
            return None

        return self.to_task(row)

    def create(self, title: str) -> Task:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (?, 0)
                """,
                (title,),
            )

            task_id = cursor.lastrowid
            connection.commit()

            row = connection.execute(
                """
                SELECT id, title, done
                FROM tasks
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()

        return self.to_task(row)

    def update(
        self,
        task_id: int,
        changes: dict[str, object],
    ) -> Task | None:
        assignments = []
        values = []

        if "title" in changes:
            assignments.append("title = ?")
            values.append(changes["title"])

        if "done" in changes:
            assignments.append("done = ?")
            values.append(int(changes["done"]))

        values.append(task_id)

        query = (
            "UPDATE tasks SET "
            + ", ".join(assignments)
            + " WHERE id = ?"
        )

        with self.connect() as connection:
            cursor = connection.execute(
                query,
                values,
            )

            if cursor.rowcount == 0:
                return None

            connection.commit()

        return self.get_by_id(task_id)

    def delete(self, task_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM tasks
                WHERE id = ?
                """,
                (task_id,),
            )

            connection.commit()

        return cursor.rowcount > 0