from collections.abc import Sequence

from ..models import Schedule
from .schedule_utils import planned_minutes


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
        duration = planned_minutes(schedule.start_time, schedule.end_time)
        total_planned_minutes += duration
        if schedule.is_completed:
            completed_planned_minutes += duration

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
