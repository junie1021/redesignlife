import re
from datetime import date as DateValue
from datetime import time as TimeValue
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


HHMM_PATTERN = r"(?:[01]\d|2[0-3]):[0-5]\d"
DATE_PATTERN = r"\d{4}-\d{2}-\d{2}"


def validate_hhmm(value: object) -> object:
    if not isinstance(value, str) or re.fullmatch(HHMM_PATTERN, value) is None:
        raise ValueError("time must use HH:MM format")
    return value


def normalize_ai_hhmm(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("time must use HH:MM format")
    match = re.fullmatch(f"({HHMM_PATTERN})(?::00)?", value)
    if match is None:
        raise ValueError("time must use HH:MM format")
    return match.group(1)


def validate_date_string(value: object) -> object:
    if not isinstance(value, str) or re.fullmatch(DATE_PATTERN, value) is None:
        raise ValueError("date must use YYYY-MM-DD format")
    return value


def validate_non_blank(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("value must not be blank")
    return stripped


class RecoveryRequest(BaseModel):
    user_id: str = Field(min_length=1)
    current_time: TimeValue

    @field_validator("current_time", mode="before")
    @classmethod
    def validate_current_time(cls, value: object) -> object:
        return validate_hhmm(value)


class RecoveryPlanItem(BaseModel):
    source_schedule_id: str | None
    title: str
    start_time: str
    end_time: str
    reason: str

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_times(cls, value: object) -> object:
        return normalize_ai_hhmm(value)

    @field_validator("title", "reason")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return validate_non_blank(value)


class MoveToTomorrowItem(BaseModel):
    source_schedule_id: str | None
    title: str
    estimated_minutes: int = Field(gt=0)
    reason: str

    @field_validator("title", "reason")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return validate_non_blank(value)


class RecoveryAIOutput(BaseModel):
    summary: str
    strengths: list[str]
    improvements: list[str]
    today_recovery_plan: list[RecoveryPlanItem]
    move_to_tomorrow: list[MoveToTomorrowItem]
    advice: str


class RecoveryData(RecoveryAIOutput):
    date: str


class RecoveryResponse(BaseModel):
    success: bool
    data: RecoveryData


class OptimizeTask(BaseModel):
    title: str
    estimated_minutes: int = Field(gt=0)
    priority: int = Field(ge=1, le=3)
    category: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return validate_non_blank(value)


class OptimizeRequest(BaseModel):
    user_id: str = Field(min_length=1)
    date: DateValue
    available_start_time: TimeValue
    available_end_time: TimeValue
    tasks: list[OptimizeTask] = Field(min_length=1)

    @field_validator("date", mode="before")
    @classmethod
    def validate_date_format(cls, value: object) -> object:
        return validate_date_string(value)

    @field_validator("available_start_time", "available_end_time", mode="before")
    @classmethod
    def validate_time_format(cls, value: object) -> object:
        return validate_hhmm(value)

    @model_validator(mode="after")
    def validate_available_range(self) -> "OptimizeRequest":
        if self.available_start_time >= self.available_end_time:
            raise ValueError("available_start_time must be before available_end_time")
        return self


class OptimizedSchedule(BaseModel):
    title: str
    start_time: str
    end_time: str
    priority: int = Field(ge=1, le=3)
    schedule_type: Literal["ADJUSTABLE"]
    category: str | None
    reason: str

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_times(cls, value: object) -> object:
        return normalize_ai_hhmm(value)

    @field_validator("title", "reason")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return validate_non_blank(value)


class UnscheduledTask(BaseModel):
    title: str
    estimated_minutes: int = Field(gt=0)
    reason: str

    @field_validator("title", "reason")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return validate_non_blank(value)


class OptimizeAIOutput(BaseModel):
    summary: str
    optimized_schedules: list[OptimizedSchedule]
    unscheduled_tasks: list[UnscheduledTask]
    advice: str


class OptimizeData(OptimizeAIOutput):
    date: str


class OptimizeResponse(BaseModel):
    success: bool
    data: OptimizeData
