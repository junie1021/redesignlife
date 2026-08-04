import pytest
from pydantic import ValidationError

from backend.ai_schemas import OptimizedSchedule, RecoveryPlanItem


def test_optimized_schedule_normalizes_zero_seconds() -> None:
    schedule = OptimizedSchedule(
        title="presentation",
        start_time="19:00:00",
        end_time="20:00:00",
        priority=3,
        schedule_type="ADJUSTABLE",
        category="project",
        reason="Complete the requested task.",
    )

    assert schedule.start_time == "19:00"
    assert schedule.end_time == "20:00"


def test_recovery_plan_normalizes_zero_seconds() -> None:
    plan = RecoveryPlanItem(
        source_schedule_id=None,
        title="presentation",
        start_time="19:00:00",
        end_time="20:00:00",
        reason="Recover the missed task.",
    )

    assert plan.start_time == "19:00"
    assert plan.end_time == "20:00"


def test_ai_schedule_rejects_nonzero_seconds() -> None:
    with pytest.raises(ValidationError, match="time must use HH:MM format"):
        OptimizedSchedule(
            title="presentation",
            start_time="19:00:30",
            end_time="20:00:00",
            priority=3,
            schedule_type="ADJUSTABLE",
            category="project",
            reason="Complete the requested task.",
        )
