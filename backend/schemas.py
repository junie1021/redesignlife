from datetime import date as DateValue
from datetime import time as TimeValue
import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class TestResultRequest(BaseModel):
    answers: list[str]


class TestResultData(BaseModel):
    user_id: str
    user_type: str


class TestResultResponse(BaseModel):
    success: bool
    data: TestResultData


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool
    error: ErrorDetail


class ScheduleCreateRequest(BaseModel):
    user_id: str = Field(min_length=1)
    date: DateValue
    title: str
    start_time: TimeValue
    end_time: TimeValue
    priority: int = Field(ge=1, le=3)
    schedule_type: Literal["FIXED", "ADJUSTABLE"]

    @field_validator("date", mode="before")
    @classmethod
    def validate_date_format(cls, value: object) -> object:
        if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
            raise ValueError("date must use YYYY-MM-DD format")
        return value

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time_format(cls, value: object) -> object:
        pattern = r"(?:[01]\d|2[0-3]):[0-5]\d"
        if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
            raise ValueError("time must use HH:MM format")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        title = value.strip()
        if not title:
            raise ValueError("title must not be blank")
        return title


class ScheduleUpdateRequest(BaseModel):
    user_id: str = Field(min_length=1)
    title: str | None = None
    date: DateValue | None = None
    start_time: TimeValue | None = None
    end_time: TimeValue | None = None
    priority: int | None = Field(default=None, ge=1, le=3)
    schedule_type: Literal["FIXED", "ADJUSTABLE"] | None = None
    category: str | None = None
    is_completed: bool | None = None
    satisfaction: int | None = Field(default=None, ge=1, le=5)

    @field_validator("date", mode="before")
    @classmethod
    def validate_date_format(cls, value: object) -> object:
        if value is None:
            return value
        if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
            raise ValueError("date must use YYYY-MM-DD format")
        return value

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time_format(cls, value: object) -> object:
        if value is None:
            return value
        pattern = r"(?:[01]\d|2[0-3]):[0-5]\d"
        if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
            raise ValueError("time must use HH:MM format")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        title = value.strip()
        if not title:
            raise ValueError("title must not be blank")
        return title

    @model_validator(mode="after")
    def reject_null_for_non_nullable_fields(self) -> "ScheduleUpdateRequest":
        nullable_fields = {"category", "satisfaction"}
        for field_name in self.model_fields_set - nullable_fields:
            if field_name != "user_id" and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} must not be null")
        return self


class ScheduleConflictRequest(BaseModel):
    user_id: str = Field(min_length=1)
    date: DateValue
    start_time: TimeValue
    end_time: TimeValue
    exclude_schedule_id: str | None = None

    @field_validator("date", mode="before")
    @classmethod
    def validate_date_format(cls, value: object) -> object:
        if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
            raise ValueError("date must use YYYY-MM-DD format")
        return value

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time_format(cls, value: object) -> object:
        pattern = r"(?:[01]\d|2[0-3]):[0-5]\d"
        if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
            raise ValueError("time must use HH:MM format")
        return value


class ScheduleItem(BaseModel):
    schedule_id: str
    title: str
    start_time: str
    end_time: str
    priority: int
    schedule_type: str
    category: str | None
    is_completed: bool
    satisfaction: int | None


class ScheduleData(ScheduleItem):
    user_id: str
    date: str


class ScheduleCreateResponse(BaseModel):
    success: bool
    data: ScheduleData


class ScheduleListData(BaseModel):
    date: str
    schedules: list[ScheduleItem]


class ScheduleListResponse(BaseModel):
    success: bool
    data: ScheduleListData


class ScheduleDeleteData(BaseModel):
    schedule_id: str
    message: str


class ScheduleDeleteResponse(BaseModel):
    success: bool
    data: ScheduleDeleteData


class ScheduleConflictItem(BaseModel):
    schedule_id: str
    title: str
    start_time: str
    end_time: str
    schedule_type: str


class ScheduleConflictData(BaseModel):
    has_conflict: bool
    conflict_count: int
    conflicts: list[ScheduleConflictItem]


class ScheduleConflictResponse(BaseModel):
    success: bool
    data: ScheduleConflictData


class DailySummaryData(BaseModel):
    user_id: str
    user_type: str
    date: str
    total_count: int
    completed_count: int
    incomplete_count: int
    completion_rate: float
    average_satisfaction: float | None
    fixed_count: int
    adjustable_count: int
    total_planned_minutes: int
    completed_planned_minutes: int


class DailySummaryResponse(BaseModel):
    success: bool
    data: DailySummaryData
