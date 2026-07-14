from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, StrictBool, StrictStr

app = FastAPI()

tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Publish project to GitHub", "done": True},
]


class TaskCreate(BaseModel):
    title: StrictStr | None = None


class TaskUpdate(BaseModel):
    title: StrictStr | None = None
    done: StrictBool | None = None


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exception: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body"},
    )


def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


@app.get("/")
def get_api_information():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks")
def get_all_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    return task


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    if payload.title is None or not payload.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"},
        )

    next_id = max(task["id"] for task in tasks) + 1

    new_task = {
        "id": next_id,
        "title": payload.title.strip(),
        "done": False,
    }

    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    task = find_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"},
        )

    if "title" in changes:
        title = changes["title"]

        if title is None or not title.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title cannot be empty"},
            )

        task["title"] = title.strip()

    if "done" in changes:
        if changes["done"] is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be true or false"},
            )

        task["done"] = changes["done"]

    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    tasks.remove(task)
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)