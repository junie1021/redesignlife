import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import models  # noqa: F401 - registers database models on application startup
from .database import Base, engine
from .routers.daily_summary import router as daily_summary_router
from .routers.schedules import INVALID_SCHEDULE_RESPONSE, router as schedules_router
from .routers.test_result import INVALID_ANSWERS_RESPONSE, router as test_result_router


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
    content = (
        INVALID_ANSWERS_RESPONSE
        if request.url.path == "/api/test-result"
        else INVALID_SCHEDULE_RESPONSE
    )
    return JSONResponse(status_code=400, content=content)


app.include_router(test_result_router)
app.include_router(schedules_router)
app.include_router(daily_summary_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
