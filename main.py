from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, StrictBool, StrictStr


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

app = FastAPI(
    title="Task API",
    version="1.0",
    description=(
        "A simple CRUD API for managing to-do tasks. "
        "The data is stored in memory and will reset "
        "whenever the server restarts."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)


# =========================================================
# IN-MEMORY DATA
# =========================================================

tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False,
    },
    {
        "id": 2,
        "title": "Build a CRUD API",
        "done": False,
    },
    {
        "id": 3,
        "title": "Publish project to GitHub",
        "done": True,
    },
]


# =========================================================
# REQUEST MODELS
# =========================================================

class TaskCreate(BaseModel):
    title: StrictStr | None = None


class TaskUpdate(BaseModel):
    title: StrictStr | None = None
    done: StrictBool | None = None


# =========================================================
# ERROR HANDLER
# =========================================================

@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exception: RequestValidationError,
):
    """
    Converts FastAPI's default 422 validation response
    into the required 400 Bad Request response.
    """

    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request body",
        },
    )


# =========================================================
# HELPER FUNCTION
# =========================================================

def find_task(task_id: int):
    """
    Finds a task by its ID.

    Returns the task when found.
    Returns None when the task does not exist.
    """

    for task in tasks:
        if task["id"] == task_id:
            return task

    return None


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get(
    "/",
    summary="Get API information",
    description=(
        "Returns basic information about the API, including "
        "its name, version, and main task endpoint."
    ),
    response_description="Basic API information",
    tags=["General"],
)
def get_api_information():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": [
            "/tasks",
        ],
    }


# =========================================================
# HEALTH ENDPOINT
# =========================================================

@app.get(
    "/health",
    summary="Check server health",
    description="Checks whether the Task API server is running.",
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
    description="Returns every task currently stored in memory.",
    response_description="A list containing all tasks",
    tags=["Tasks"],
)
def get_all_tasks():
    return tasks


# =========================================================
# READ ONE TASK
# =========================================================

@app.get(
    "/tasks/{task_id}",
    summary="Get a task by ID",
    description=(
        "Returns one task based on its ID. "
        "Returns 404 when the task does not exist."
    ),
    response_description="The requested task",
    responses={
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Task 99 not found",
                    }
                }
            },
        }
    },
    tags=["Tasks"],
)
def get_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Task {task_id} not found",
            },
        )

    return task


# =========================================================
# CREATE TASK
# =========================================================

@app.post(
    "/tasks",
    status_code=201,
    summary="Create a new task",
    description=(
        "Creates a new task. The server automatically gives "
        "the task a new ID and sets done to false."
    ),
    response_description="The newly created task",
    responses={
        201: {
            "description": "Task successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 4,
                        "title": "Buy milk",
                        "done": False,
                    }
                }
            },
        },
        400: {
            "description": "Invalid title or request body",
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

    next_id = max(
        task["id"] for task in tasks
    ) + 1 if tasks else 1

    new_task = {
        "id": next_id,
        "title": payload.title.strip(),
        "done": False,
    }

    tasks.append(new_task)

    return new_task


# =========================================================
# UPDATE TASK
# =========================================================

@app.put(
    "/tasks/{task_id}",
    summary="Update an existing task",
    description=(
        "Updates the title, done status, or both fields "
        "of an existing task."
    ),
    response_description="The updated task",
    responses={
        200: {
            "description": "Task successfully updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Finish CRUD API",
                        "done": True,
                    }
                }
            },
        },
        400: {
            "description": "Invalid or empty request body",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Request body cannot be empty",
                    }
                }
            },
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Task 99 not found",
                    }
                }
            },
        },
    },
    tags=["Tasks"],
)
def update_task(task_id: int, payload: TaskUpdate):
    task = find_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Task {task_id} not found",
            },
        )

    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Request body cannot be empty",
            },
        )

    if "title" in changes:
        title = changes["title"]

        if title is None or not title.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Title cannot be empty",
                },
            )

        task["title"] = title.strip()

    if "done" in changes:
        done = changes["done"]

        if done is None:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Done must be true or false",
                },
            )

        task["done"] = done

    return task


# =========================================================
# DELETE TASK
# =========================================================

@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete an existing task",
    description=(
        "Removes a task from memory based on its ID. "
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
                        "error": "Task 99 not found",
                    }
                }
            },
        },
    },
    tags=["Tasks"],
)
def delete_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Task {task_id} not found",
            },
        )

    tasks.remove(task)

    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)