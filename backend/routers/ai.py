from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..ai_schemas import (
    DailyAnalysisRequest,
    DailyAnalysisResponse,
    OptimizeRequest,
    OptimizeResponse,
    RecoveryRequest,
    RecoveryResponse,
)
from ..database import get_db
from ..errors import (
    AI_INVALID_OUTPUT_RESPONSE,
    AI_NOT_CONFIGURED_RESPONSE,
    AI_SERVICE_ERROR_RESPONSE,
    AI_TIMEOUT_RESPONSE,
    NO_SCHEDULES_RESPONSE,
    USER_NOT_FOUND_RESPONSE,
)
from ..models import Schedule, User
from ..schemas import ErrorResponse
from ..services.ai_service import (
    AINotConfiguredError,
    AIOutputValidationError,
    AIService,
    AIServiceError,
    AIServiceTimeoutError,
    get_ai_service,
)
from ..services.ai_validation import (
    AIResultValidationError,
    validate_optimize_output,
    validate_recovery_output,
)
from ..services.statistics import calculate_daily_statistics


router = APIRouter(prefix="/api", tags=["ai-planning"])


def ai_error_response(error: Exception) -> JSONResponse:
    if isinstance(error, AINotConfiguredError):
        return JSONResponse(status_code=503, content=AI_NOT_CONFIGURED_RESPONSE)
    if isinstance(error, AIServiceTimeoutError):
        return JSONResponse(status_code=504, content=AI_TIMEOUT_RESPONSE)
    if isinstance(error, (AIOutputValidationError, AIResultValidationError)):
        return JSONResponse(status_code=502, content=AI_INVALID_OUTPUT_RESPONSE)
    return JSONResponse(status_code=502, content=AI_SERVICE_ERROR_RESPONSE)


def schedule_context(schedule: Schedule) -> dict[str, object]:
    return {
        "schedule_id": schedule.id,
        "title": schedule.title,
        "start_time": schedule.start_time.strftime("%H:%M"),
        "end_time": schedule.end_time.strftime("%H:%M"),
        "priority": schedule.priority,
        "schedule_type": schedule.schedule_type,
        "category": schedule.category,
        "is_completed": schedule.is_completed,
        "satisfaction": schedule.satisfaction,
    }


@router.post(
    "/days/{date}/analysis",
    response_model=DailyAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
async def analyze_day(
    analysis_date: Annotated[date, Path(alias="date")],
    payload: DailyAnalysisRequest,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
) -> DailyAnalysisResponse | JSONResponse:
    user = db.get(User, payload.user_id)
    if user is None:
        return JSONResponse(status_code=404, content=USER_NOT_FOUND_RESPONSE)

    context = {
        "date": analysis_date.isoformat(),
        "user_type": user.user_type,
        "tasks": [task.model_dump(mode="json") for task in payload.tasks],
    }
    try:
        output = await ai_service.analyze_day(context)
    except (
        AINotConfiguredError,
        AIServiceTimeoutError,
        AIServiceError,
        AIOutputValidationError,
    ) as error:
        return ai_error_response(error)

    return DailyAnalysisResponse(
        success=True,
        data={"date": analysis_date.isoformat(), **output.model_dump()},
    )


@router.post(
    "/days/{date}/recovery",
    response_model=RecoveryResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
async def create_recovery_plan(
    recovery_date: Annotated[date, Path(alias="date")],
    payload: RecoveryRequest,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
) -> RecoveryResponse | JSONResponse:
    user = db.get(User, payload.user_id)
    if user is None:
        return JSONResponse(status_code=404, content=USER_NOT_FOUND_RESPONSE)

    statement = (
        select(Schedule)
        .where(
            Schedule.user_id == user.id,
            Schedule.date == recovery_date,
        )
        .order_by(Schedule.start_time)
    )
    schedules = list(db.scalars(statement))
    if not schedules:
        return JSONResponse(status_code=400, content=NO_SCHEDULES_RESPONSE)

    context = {
        "date": recovery_date.isoformat(),
        "current_time": payload.current_time.strftime("%H:%M"),
        "user_type": user.user_type,
        "statistics": calculate_daily_statistics(schedules),
        "schedules": [schedule_context(schedule) for schedule in schedules],
    }
    try:
        output = await ai_service.generate_recovery(context)
        validate_recovery_output(output, schedules, payload.current_time)
    except (
        AINotConfiguredError,
        AIServiceTimeoutError,
        AIServiceError,
        AIOutputValidationError,
        AIResultValidationError,
    ) as error:
        return ai_error_response(error)

    return RecoveryResponse(
        success=True,
        data={"date": recovery_date.isoformat(), **output.model_dump()},
    )


@router.post(
    "/plans/optimize",
    response_model=OptimizeResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
async def optimize_plan(
    payload: OptimizeRequest,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
) -> OptimizeResponse | JSONResponse:
    user = db.get(User, payload.user_id)
    if user is None:
        return JSONResponse(status_code=404, content=USER_NOT_FOUND_RESPONSE)

    statement = (
        select(Schedule)
        .where(
            Schedule.user_id == user.id,
            Schedule.date == payload.date,
            Schedule.schedule_type == "FIXED",
        )
        .order_by(Schedule.start_time)
    )
    fixed_schedules = list(db.scalars(statement))
    all_fixed_schedules = [*fixed_schedules, *payload.fixed_schedules]
    context = {
        "date": payload.date.isoformat(),
        "available_start_time": payload.available_start_time.strftime("%H:%M"),
        "available_end_time": payload.available_end_time.strftime("%H:%M"),
        "user_type": user.user_type,
        "tasks": [task.model_dump() for task in payload.tasks],
        "fixed_schedules": [
            schedule_context(schedule) for schedule in fixed_schedules
        ] + [schedule.model_dump(mode="json") for schedule in payload.fixed_schedules],
    }

    retry_feedback: str | None = None
    output = None
    for _ in range(2):
        try:
            output = await ai_service.optimize_plan(context, retry_feedback)
            validate_optimize_output(output, payload, all_fixed_schedules)
            break
        except AIResultValidationError as error:
            retry_feedback = str(error)
        except (
            AINotConfiguredError,
            AIServiceTimeoutError,
            AIServiceError,
            AIOutputValidationError,
        ) as error:
            return ai_error_response(error)
    else:
        return ai_error_response(AIResultValidationError(retry_feedback))

    return OptimizeResponse(
        success=True,
        data={"date": payload.date.isoformat(), **output.model_dump()},
    )
