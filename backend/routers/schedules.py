from datetime import date, datetime, time, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Schedule, User
from ..schemas import (
    ErrorResponse,
    ScheduleCreateRequest,
    ScheduleCreateResponse,
    ScheduleConflictItem,
    ScheduleConflictRequest,
    ScheduleConflictResponse,
    ScheduleItem,
    ScheduleListResponse,
    ScheduleData,
    ScheduleDeleteResponse,
    ScheduleUpdateRequest,
)


router = APIRouter(prefix="/api", tags=["schedules"])

INVALID_SCHEDULE_RESPONSE = {
    "success": False,
    "error": {
        "code": "INVALID_SCHEDULE_DATA",
        "message": "일정 정보를 올바르게 입력해주세요.",
    },
}
USER_NOT_FOUND_RESPONSE = {
    "success": False,
    "error": {
        "code": "USER_NOT_FOUND",
        "message": "해당 사용자를 찾을 수 없습니다.",
    },
}
INVALID_TIME_RANGE_RESPONSE = {
    "success": False,
    "error": {
        "code": "INVALID_TIME_RANGE",
        "message": "시작 시간은 종료 시간보다 빨라야 합니다.",
    },
}
SCHEDULE_NOT_FOUND_RESPONSE = {
    "success": False,
    "error": {
        "code": "SCHEDULE_NOT_FOUND",
        "message": "해당 일정을 찾을 수 없습니다.",
    },
}
NO_UPDATE_FIELDS_RESPONSE = {
    "success": False,
    "error": {
        "code": "NO_UPDATE_FIELDS",
        "message": "수정할 항목을 입력해주세요.",
    },
}


def schedule_to_item(schedule: Schedule) -> ScheduleItem:
    return ScheduleItem(
        schedule_id=schedule.id,
        title=schedule.title,
        start_time=schedule.start_time.strftime("%H:%M"),
        end_time=schedule.end_time.strftime("%H:%M"),
        priority=schedule.priority,
        schedule_type=schedule.schedule_type,
        category=schedule.category,
        is_completed=schedule.is_completed,
        satisfaction=schedule.satisfaction,
    )


def schedule_to_data(schedule: Schedule) -> ScheduleData:
    return ScheduleData(
        **schedule_to_item(schedule).model_dump(),
        user_id=schedule.user_id,
        date=schedule.date.isoformat(),
    )


def time_ranges_overlap(
    first_start: time,
    first_end: time,
    second_start: time,
    second_end: time,
) -> bool:
    return first_start < second_end and first_end > second_start


@router.post(
    "/schedules",
    response_model=ScheduleCreateResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def create_schedule(
    payload: ScheduleCreateRequest,
    db: Session = Depends(get_db),
) -> ScheduleCreateResponse | JSONResponse:
    user = db.get(User, payload.user_id)
    if user is None:
        return JSONResponse(status_code=404, content=USER_NOT_FOUND_RESPONSE)

    if payload.start_time >= payload.end_time:
        return JSONResponse(status_code=400, content=INVALID_TIME_RANGE_RESPONSE)

    schedule = Schedule(
        id=str(uuid4()),
        user_id=user.id,
        date=payload.date,
        title=payload.title,
        start_time=payload.start_time,
        end_time=payload.end_time,
        priority=payload.priority,
        schedule_type=payload.schedule_type,
        category=None,
        is_completed=False,
        satisfaction=None,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return ScheduleCreateResponse(
        success=True,
        data=schedule_to_data(schedule),
    )


@router.get(
    "/schedules",
    response_model=ScheduleListResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_schedules(
    user_id: Annotated[str, Query(min_length=1)],
    schedule_date: Annotated[date, Query(alias="date")],
    db: Session = Depends(get_db),
) -> ScheduleListResponse | JSONResponse:
    user = db.get(User, user_id)
    if user is None:
        return JSONResponse(status_code=404, content=USER_NOT_FOUND_RESPONSE)

    statement = (
        select(Schedule)
        .where(Schedule.user_id == user_id, Schedule.date == schedule_date)
        .order_by(Schedule.start_time)
    )
    schedules = db.scalars(statement).all()

    return ScheduleListResponse(
        success=True,
        data={
            "date": schedule_date.isoformat(),
            "schedules": [schedule_to_item(schedule) for schedule in schedules],
        },
    )


@router.post(
    "/schedules/check-conflicts",
    response_model=ScheduleConflictResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def check_schedule_conflicts(
    payload: ScheduleConflictRequest,
    db: Session = Depends(get_db),
) -> ScheduleConflictResponse | JSONResponse:
    user = db.get(User, payload.user_id)
    if user is None:
        return JSONResponse(status_code=404, content=USER_NOT_FOUND_RESPONSE)

    if payload.start_time >= payload.end_time:
        return JSONResponse(status_code=400, content=INVALID_TIME_RANGE_RESPONSE)

    statement = select(Schedule).where(
        Schedule.user_id == payload.user_id,
        Schedule.date == payload.date,
    )
    if payload.exclude_schedule_id is not None:
        statement = statement.where(Schedule.id != payload.exclude_schedule_id)
    statement = statement.order_by(Schedule.start_time)

    conflicts = [
        schedule
        for schedule in db.scalars(statement)
        if time_ranges_overlap(
            schedule.start_time,
            schedule.end_time,
            payload.start_time,
            payload.end_time,
        )
    ]

    return ScheduleConflictResponse(
        success=True,
        data={
            "has_conflict": bool(conflicts),
            "conflict_count": len(conflicts),
            "conflicts": [
                ScheduleConflictItem(
                    schedule_id=schedule.id,
                    title=schedule.title,
                    start_time=schedule.start_time.strftime("%H:%M"),
                    end_time=schedule.end_time.strftime("%H:%M"),
                    schedule_type=schedule.schedule_type,
                )
                for schedule in conflicts
            ],
        },
    )


@router.patch(
    "/schedules/{schedule_id}",
    response_model=ScheduleCreateResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def update_schedule(
    schedule_id: str,
    payload: ScheduleUpdateRequest,
    db: Session = Depends(get_db),
) -> ScheduleCreateResponse | JSONResponse:
    schedule = db.get(Schedule, schedule_id)
    if schedule is None or schedule.user_id != payload.user_id:
        return JSONResponse(status_code=404, content=SCHEDULE_NOT_FOUND_RESPONSE)

    updates = payload.model_dump(exclude_unset=True)
    updates.pop("user_id")
    if not updates:
        return JSONResponse(status_code=400, content=NO_UPDATE_FIELDS_RESPONSE)

    start_time = updates.get("start_time", schedule.start_time)
    end_time = updates.get("end_time", schedule.end_time)
    if start_time >= end_time:
        return JSONResponse(status_code=400, content=INVALID_TIME_RANGE_RESPONSE)

    for field_name, value in updates.items():
        setattr(schedule, field_name, value)
    schedule.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(schedule)

    return ScheduleCreateResponse(success=True, data=schedule_to_data(schedule))


@router.delete(
    "/schedules/{schedule_id}",
    response_model=ScheduleDeleteResponse,
    responses={404: {"model": ErrorResponse}},
)
def delete_schedule(
    schedule_id: Annotated[str, Path(min_length=1)],
    user_id: Annotated[str, Query(min_length=1)],
    db: Session = Depends(get_db),
) -> ScheduleDeleteResponse | JSONResponse:
    statement = select(Schedule).where(
        Schedule.id == schedule_id,
        Schedule.user_id == user_id,
    )
    schedule = db.scalar(statement)
    if schedule is None:
        return JSONResponse(status_code=404, content=SCHEDULE_NOT_FOUND_RESPONSE)

    db.delete(schedule)
    db.commit()

    return ScheduleDeleteResponse(
        success=True,
        data={
            "schedule_id": schedule_id,
            "message": "일정이 삭제되었습니다.",
        },
    )
