from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors import ApiError
from app.routes.tasks import router as task_router


app = FastAPI(
    title="Task API",
    version="3.0",
    description=(
        "A layered CRUD API whose repository "
        "can be changed without changing its routes."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(ApiError)
async def api_error_handler(
    request: Request,
    exception: ApiError,
):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": exception.message,
        },
    )


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


@app.get(
    "/",
    summary="Get API information",
    tags=["General"],
)
def get_api_information():
    return {
        "name": "Task API",
        "version": "3.0",
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


app.include_router(task_router)