from datetime import datetime, time

from ..ai_schemas import OptimizeAIOutput, OptimizeRequest, RecoveryAIOutput
from ..models import Schedule
from .schedule_utils import planned_minutes, time_ranges_overlap


class AIResultValidationError(ValueError):
    pass


def parse_hhmm(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def validate_recovery_output(
    output: RecoveryAIOutput,
    schedules: list[Schedule],
    current_time: time,
) -> None:
    allowed_ids = {schedule.id for schedule in schedules}
    fixed_schedules = [
        schedule for schedule in schedules if schedule.schedule_type == "FIXED"
    ]
    recovery_ranges: list[tuple[time, time]] = []

    for item in output.today_recovery_plan:
        if item.source_schedule_id is not None and item.source_schedule_id not in allowed_ids:
            raise AIResultValidationError("unknown source_schedule_id")
        start_time = parse_hhmm(item.start_time)
        end_time = parse_hhmm(item.end_time)
        if start_time < current_time or start_time >= end_time:
            raise AIResultValidationError("invalid recovery time range")
        if any(
            time_ranges_overlap(
                start_time,
                end_time,
                fixed.start_time,
                fixed.end_time,
            )
            for fixed in fixed_schedules
        ):
            raise AIResultValidationError("recovery overlaps a fixed schedule")
        if any(
            time_ranges_overlap(start_time, end_time, other_start, other_end)
            for other_start, other_end in recovery_ranges
        ):
            raise AIResultValidationError("recovery items overlap")
        recovery_ranges.append((start_time, end_time))

    for item in output.move_to_tomorrow:
        if item.source_schedule_id is not None and item.source_schedule_id not in allowed_ids:
            raise AIResultValidationError("unknown source_schedule_id")


def validate_optimize_output(
    output: OptimizeAIOutput,
    request: OptimizeRequest,
    fixed_schedules: list[Schedule],
) -> None:
    unmatched_tasks = list(request.tasks)
    optimized_ranges: list[tuple[time, time]] = []

    for item in output.optimized_schedules:
        start_time = parse_hhmm(item.start_time)
        end_time = parse_hhmm(item.end_time)
        if (
            start_time < request.available_start_time
            or end_time > request.available_end_time
            or start_time >= end_time
        ):
            raise AIResultValidationError("optimized schedule is outside available time")
        if any(
            time_ranges_overlap(
                start_time,
                end_time,
                fixed.start_time,
                fixed.end_time,
            )
            for fixed in fixed_schedules
        ):
            raise AIResultValidationError("optimized schedule overlaps a fixed schedule")
        if any(
            time_ranges_overlap(start_time, end_time, other_start, other_end)
            for other_start, other_end in optimized_ranges
        ):
            raise AIResultValidationError("optimized schedules overlap")

        matching_index = next(
            (
                index
                for index, task in enumerate(unmatched_tasks)
                if task.title == item.title
                and task.priority == item.priority
                and task.category == item.category
                and task.estimated_minutes == planned_minutes(start_time, end_time)
            ),
            None,
        )
        if matching_index is None:
            raise AIResultValidationError("optimized schedule does not match an input task")
        unmatched_tasks.pop(matching_index)
        optimized_ranges.append((start_time, end_time))

    for item in output.unscheduled_tasks:
        matching_index = next(
            (
                index
                for index, task in enumerate(unmatched_tasks)
                if task.title == item.title
                and task.estimated_minutes == item.estimated_minutes
            ),
            None,
        )
        if matching_index is None:
            raise AIResultValidationError("unscheduled task does not match an input task")
        unmatched_tasks.pop(matching_index)

    if unmatched_tasks:
        raise AIResultValidationError("AI omitted input tasks")
