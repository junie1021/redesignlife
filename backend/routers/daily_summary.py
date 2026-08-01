from collections.abc import Sequence
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Schedule, User
from ..schemas import DailySummaryResponse, ErrorResponse
from .schedules import USER_NOT_FOUND_RESPONSE


router = APIRouter(prefix="/api", tags=["daily-summary"])


def calculate_daily_statistics(
    schedules: Sequence[Schedule],
) -> dict[str, int | float | None]:
    total_count = len(schedules)
    completed_count = sum(schedule.is_completed for schedule in schedules)
    satisfactions = [
        schedule.satisfaction
        for schedule in schedules
        if schedule.satisfaction is not None
    ]

    total_planned_minutes = 0
    completed_planned_minutes = 0
    for schedule in schedules:
        start_minutes = schedule.start_time.hour * 60 + schedule.start_time.minute
        end_minutes = schedule.end_time.hour * 60 + schedule.end_time.minute
        planned_minutes = end_minutes - start_minutes
        total_planned_minutes += planned_minutes
        if schedule.is_completed:
            completed_planned_minutes += planned_minutes

    return {
        "total_count": total_count,
        "completed_count": completed_count,
        "incomplete_count": total_count - completed_count,
        "completion_rate": (
            round(completed_count / total_count * 100, 2) if total_count else 0.0
        ),
        "average_satisfaction": (
            round(sum(satisfactions) / len(satisfactions), 2)
            if satisfactions
            else None
        ),
        "fixed_count": sum(
            schedule.schedule_type == "FIXED" for schedule in schedules
        ),
        "adjustable_count": sum(
            schedule.schedule_type == "ADJUSTABLE" for schedule in schedules
        ),
        "total_planned_minutes": total_planned_minutes,
        "completed_planned_minutes": completed_planned_minutes,
    }


@router.get(
    "/daily-summary",
    response_model=DailySummaryResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_daily_summary(
    user_id: Annotated[str, Query(min_length=1)],
    summary_date: Annotated[date, Query(alias="date")],
    db: Session = Depends(get_db),
) -> DailySummaryResponse | JSONResponse:
    user = db.get(User, user_id)
    if user is None:
        return JSONResponse(status_code=404, content=USER_NOT_FOUND_RESPONSE)

    statement = select(Schedule).where(
        Schedule.user_id == user_id,
        Schedule.date == summary_date,
    )
    schedules = list(db.scalars(statement))
    statistics = calculate_daily_statistics(schedules)

    return DailySummaryResponse(
        success=True,
        data={
            "user_id": user.id,
            "user_type": user.user_type,
            "date": summary_date.isoformat(),
            **statistics,
        },
    )
