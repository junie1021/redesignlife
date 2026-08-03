import os
from contextlib import asynccontextmanager

import uvicorn
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
    INVALID_ANALYSIS_RESPONSE,
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


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Redesign Life API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
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
    elif request.url.path.endswith("/analysis"):
        content = INVALID_ANALYSIS_RESPONSE
    else:
        content = INVALID_SCHEDULE_RESPONSE
    return JSONResponse(status_code=400, content=content)


app.include_router(users_router)
app.include_router(schedules_router)
app.include_router(daily_summary_router)
app.include_router(ai_router)


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
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
