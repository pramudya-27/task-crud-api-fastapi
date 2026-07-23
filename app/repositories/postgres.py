from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.domain import Task


class PostgresTaskRepository:
    def __init__(
        self,
        database_url: str,
    ) -> None:
        self.database_url = database_url

    def connect(self):
        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
        )

    @staticmethod
    def to_task(
        row: dict[str, Any],
    ) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            done=row["done"],
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
                WHERE id = %s
                """,
                (task_id,),
            ).fetchone()

        if row is None:
            return None

        return self.to_task(row)

    def create(self, title: str) -> Task:
        with self.connect() as connection:
            row = connection.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, FALSE)
                RETURNING id, title, done
                """,
                (title,),
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
            assignments.append("title = %s")
            values.append(changes["title"])

        if "done" in changes:
            assignments.append("done = %s")
            values.append(changes["done"])

        values.append(task_id)

        query = (
            "UPDATE tasks SET "
            + ", ".join(assignments)
            + """
              WHERE id = %s
              RETURNING id, title, done
            """
        )

        with self.connect() as connection:
            row = connection.execute(
                query,
                values,
            ).fetchone()

        if row is None:
            return None

        return self.to_task(row)

    def delete(self, task_id: int) -> bool:
        with self.connect() as connection:
            row = connection.execute(
                """
                DELETE FROM tasks
                WHERE id = %s
                RETURNING id
                """,
                (task_id,),
            ).fetchone()

        return row is not None