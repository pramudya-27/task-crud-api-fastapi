from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.cache import create_redis_client
from app.errors import ApiError
from app.routes.tasks import router as task_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = create_redis_client()

    if redis_client is not None:
        redis_client.ping()

        print(
            "Redis connection: PONG",
            flush=True,
        )

        app.state.redis = redis_client

    yield

    if redis_client is not None:
        redis_client.close()

app = FastAPI(
    title="Task API",
    version="3.0",
    description=(
        "A containerized CRUD API using "
        "PostgreSQL and optional Redis."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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