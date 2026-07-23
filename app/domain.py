from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Task:
    id: int
    title: str
    done: bool