from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..errors import USER_NOT_FOUND_RESPONSE
from ..models import Schedule, User
from ..schemas import DailySummaryResponse, ErrorResponse
from ..services.statistics import calculate_daily_statistics


router = APIRouter(prefix="/api", tags=["daily-summary"])


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
