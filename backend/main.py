import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from . import models  # noqa: F401 - registers database models on application startup
from .database import Base, engine
from .errors import (
    INVALID_PLAN_RESPONSE,
    INVALID_RECOVERY_REQUEST_RESPONSE,
    INVALID_SCHEDULE_RESPONSE,
    INVALID_TEST_ANSWERS_RESPONSE,
    DATABASE_UNAVAILABLE_RESPONSE,
)
from .routers.ai import router as ai_router
from .routers.daily_summary import router as daily_summary_router
from .routers.schedules import router as schedules_router
from .routers.users import router as users_router
from .schemas import ErrorResponse, HealthResponse


def get_cors_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ORIGINS")
    if configured_origins:
        return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def get_cors_origin_regex() -> str | None:
    """Return the configured production-origin pattern for CORS."""
    configured_regex = os.getenv("CORS_ORIGIN_REGEX")
    if configured_regex is not None:
        return configured_regex.strip() or None

    return r"^https://[a-z0-9-]+\.vercel\.app$"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Redesign Life API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_origin_regex=get_cors_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    __: RequestValidationError,
) -> JSONResponse:
    if request.url.path == "/api/users/type-test":
        content = INVALID_TEST_ANSWERS_RESPONSE
    elif request.url.path.endswith("/recovery"):
        content = INVALID_RECOVERY_REQUEST_RESPONSE
    elif request.url.path == "/api/plans/optimize":
        content = INVALID_PLAN_RESPONSE
    else:
        content = INVALID_SCHEDULE_RESPONSE
    return JSONResponse(status_code=400, content=content)


app.include_router(users_router)
app.include_router(schedules_router)
app.include_router(daily_summary_router)
app.include_router(ai_router)


API_ENDPOINTS = [
    "POST /api/users/type-test",
    "POST /api/schedules",
    "GET /api/days/{date}/tasks",
    "GET /api/schedules/range",
    "POST /api/schedules/check-conflicts",
    "PATCH /api/schedules/{schedule_id}",
    "DELETE /api/schedules/{schedule_id}",
    "GET /api/daily-summary",
    "POST /api/days/{date}/recovery",
    "POST /api/plans/optimize",
]


@app.get("/api", include_in_schema=False)
@app.get("/api/", include_in_schema=False)
def api_index() -> dict[str, object]:
    """Return links and route signatures for the public API."""
    return {
        "success": True,
        "data": {
            "docs": "/docs",
            "health": "/health",
            "endpoints": API_ENDPOINTS,
        },
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"model": ErrorResponse}},
)
def health_check() -> HealthResponse | JSONResponse:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content=DATABASE_UNAVAILABLE_RESPONSE)
    return HealthResponse(
        success=True,
        data={"status": "ok", "database": "ok"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
