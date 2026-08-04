from collections.abc import Generator
from datetime import date, time
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from backend import main
from backend.ai_schemas import (
    OptimizeAIOutput,
    OptimizedSchedule,
    RecoveryAIOutput,
    RecoveryPlanItem,
    UnscheduledTask,
)
from backend.database import Base, get_db
from backend.models import Schedule, User
from backend.services.ai_service import (
    AIOutputValidationError,
    AIServiceError,
    AIServiceTimeoutError,
    get_ai_service,
)


class FakeAIService:
    def __init__(
        self,
        *,
        recovery_result: RecoveryAIOutput | Exception | None = None,
        optimize_results: list[OptimizeAIOutput | Exception] | None = None,
    ) -> None:
        self.recovery_result = recovery_result
        self.optimize_results = optimize_results or []
        self.optimize_calls = 0

    async def generate_recovery(self, context):
        if isinstance(self.recovery_result, Exception):
            raise self.recovery_result
        assert self.recovery_result is not None
        return self.recovery_result

    async def optimize_plan(self, context, retry_feedback=None):
        result = self.optimize_results[min(self.optimize_calls, len(self.optimize_results) - 1)]
        self.optimize_calls += 1
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture
def client_and_session() -> Generator[tuple[TestClient, sessionmaker[Session]], None, None]:
    with TemporaryDirectory() as temp_dir:
        database_url = f"sqlite:///{(Path(temp_dir) / 'test.db').as_posix()}"
        test_engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )
        testing_session = sessionmaker(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)

        def override_get_db():
            with testing_session() as db:
                yield db

        main.app.dependency_overrides[get_db] = override_get_db
        try:
            with TestClient(main.app) as client:
                yield client, testing_session
        finally:
            main.app.dependency_overrides.clear()
            test_engine.dispose()


def use_fake_ai(fake: FakeAIService) -> None:
    main.app.dependency_overrides[get_ai_service] = lambda: fake


def add_user(db: Session, user_type: str = "perfectionist") -> str:
    user_id = str(uuid4())
    db.add(User(id=user_id, user_type=user_type))
    return user_id


def add_schedule(
    db: Session,
    user_id: str,
    start_time: time,
    end_time: time,
    *,
    title: str = "기존 일정",
    schedule_type: str = "ADJUSTABLE",
) -> str:
    schedule_id = str(uuid4())
    db.add(
        Schedule(
            id=schedule_id,
            user_id=user_id,
            date=date(2026, 8, 2),
            title=title,
            start_time=start_time,
            end_time=end_time,
            priority=2,
            schedule_type=schedule_type,
            category=None,
            is_completed=False,
            satisfaction=None,
        )
    )
    return schedule_id


def recovery_output(
    source_schedule_id: str | None,
    *,
    start_time: str = "19:00",
    end_time: str = "20:00",
) -> RecoveryAIOutput:
    return RecoveryAIOutput(
        summary="오늘의 진행 상황을 차분히 정리했습니다.",
        strengths=["완료한 일정을 잘 마무리했습니다."],
        improvements=["남은 작업을 작게 나누면 좋습니다."],
        today_recovery_plan=[
            RecoveryPlanItem(
                source_schedule_id=source_schedule_id,
                title="보고서 초안 작성",
                start_time=start_time,
                end_time=end_time,
                reason="오늘 마칠 수 있는 핵심 범위입니다.",
            )
        ],
        move_to_tomorrow=[],
        advice="핵심 작업까지만 마치고 쉬어도 괜찮아요.",
    )


def optimize_output(
    *,
    title: str = "과제",
    start_time: str = "09:00",
    end_time: str = "10:00",
    priority: int = 3,
    category: str | None = "학교",
) -> OptimizeAIOutput:
    return OptimizeAIOutput(
        summary="우선순위가 높은 일을 먼저 배치했습니다.",
        optimized_schedules=[
            OptimizedSchedule(
                title=title,
                start_time=start_time,
                end_time=end_time,
                priority=priority,
                schedule_type="ADJUSTABLE",
                category=category,
                reason="집중하기 좋은 시간입니다.",
            )
        ],
        unscheduled_tasks=[],
        advice="일정 사이에 짧게 쉬어가세요.",
    )


def optimize_payload(user_id: str) -> dict[str, object]:
    return {
        "user_id": user_id,
        "date": "2026-08-02",
        "available_start_time": "09:00",
        "available_end_time": "18:00",
        "tasks": [
            {
                "title": "과제",
                "estimated_minutes": 60,
                "priority": 3,
                "category": "학교",
            }
        ],
    }


def test_recovery_returns_validated_plan_without_db_changes(client_and_session) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        source_id = add_schedule(db, user_id, time(16, 0), time(17, 0))
        add_schedule(
            db,
            user_id,
            time(18, 0),
            time(19, 0),
            title="저녁 고정 일정",
            schedule_type="FIXED",
        )
        db.commit()
    use_fake_ai(FakeAIService(recovery_result=recovery_output(source_id)))

    response = client.post(
        "/api/days/2026-08-02/recovery",
        json={"user_id": user_id, "current_time": "18:00"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["today_recovery_plan"][0]["start_time"] == "19:00"
    with testing_session() as db:
        assert db.scalar(select(func.count()).select_from(Schedule)) == 2


def test_recovery_returns_404_for_unknown_user(client_and_session) -> None:
    client, _ = client_and_session
    response = client.post(
        "/api/days/2026-08-02/recovery",
        json={"user_id": str(uuid4()), "current_time": "18:00"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


def test_recovery_rejects_day_without_schedules(client_and_session) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        db.commit()
    response = client.post(
        "/api/days/2026-08-02/recovery",
        json={"user_id": user_id, "current_time": "18:00"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "NO_SCHEDULES"


@pytest.mark.parametrize(
    ("path", "current_time"),
    [
        ("/api/days/2026-02-30/recovery", "18:00"),
        ("/api/days/2026-08-02/recovery", "18:00:00"),
    ],
)
def test_recovery_rejects_invalid_date_or_time(client_and_session, path, current_time) -> None:
    client, _ = client_and_session
    response = client.post(
        path,
        json={"user_id": str(uuid4()), "current_time": current_time},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_RECOVERY_REQUEST"


@pytest.mark.parametrize(
    ("error", "status_code", "error_code"),
    [
        (AIServiceTimeoutError(), 504, "AI_TIMEOUT"),
        (AIServiceError(), 502, "AI_SERVICE_ERROR"),
        (AIOutputValidationError(), 502, "AI_INVALID_OUTPUT"),
    ],
)
def test_recovery_maps_ai_errors(
    client_and_session,
    error,
    status_code,
    error_code,
) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        add_schedule(db, user_id, time(16, 0), time(17, 0))
        db.commit()
    use_fake_ai(FakeAIService(recovery_result=error))

    response = client.post(
        "/api/days/2026-08-02/recovery",
        json={"user_id": user_id, "current_time": "18:00"},
    )
    assert response.status_code == status_code
    assert response.json()["error"]["code"] == error_code


@pytest.mark.parametrize("invalid_kind", ["past", "fixed-overlap", "foreign-id"])
def test_recovery_rejects_unsafe_ai_output(client_and_session, invalid_kind) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        source_id = add_schedule(db, user_id, time(16, 0), time(17, 0))
        add_schedule(
            db, user_id, time(18, 0), time(19, 0), schedule_type="FIXED"
        )
        db.commit()

    if invalid_kind == "past":
        output = recovery_output(source_id, start_time="17:00", end_time="18:00")
    elif invalid_kind == "fixed-overlap":
        output = recovery_output(source_id, start_time="18:30", end_time="19:30")
    else:
        output = recovery_output(str(uuid4()))
    use_fake_ai(FakeAIService(recovery_result=output))

    response = client.post(
        "/api/days/2026-08-02/recovery",
        json={"user_id": user_id, "current_time": "18:00"},
    )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "AI_INVALID_OUTPUT"


def test_recovery_returns_503_without_api_key(client_and_session, monkeypatch) -> None:
    client, testing_session = client_and_session
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with testing_session() as db:
        user_id = add_user(db)
        add_schedule(db, user_id, time(16, 0), time(17, 0))
        db.commit()

    response = client.post(
        "/api/days/2026-08-02/recovery",
        json={"user_id": user_id, "current_time": "18:00"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "AI_NOT_CONFIGURED"


def test_optimize_returns_valid_plan_without_saving(client_and_session) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        add_schedule(
            db, user_id, time(12, 0), time(13, 0), schedule_type="FIXED"
        )
        db.commit()
    use_fake_ai(FakeAIService(optimize_results=[optimize_output()]))

    response = client.post("/api/plans/optimize", json=optimize_payload(user_id))

    assert response.status_code == 200
    assert response.json()["data"]["optimized_schedules"][0]["title"] == "과제"
    with testing_session() as db:
        assert db.scalar(select(func.count()).select_from(Schedule)) == 1


def test_optimize_returns_404_for_unknown_user(client_and_session) -> None:
    client, _ = client_and_session
    response = client.post(
        "/api/plans/optimize",
        json=optimize_payload(str(uuid4())),
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


@pytest.mark.parametrize(
    "change",
    [
        {"tasks": []},
        {"available_start_time": "18:00", "available_end_time": "09:00"},
        {
            "tasks": [
                {
                    "title": "과제",
                    "estimated_minutes": 0,
                    "priority": 3,
                    "category": "학교",
                }
            ]
        },
    ],
)
def test_optimize_rejects_invalid_request(client_and_session, change) -> None:
    client, _ = client_and_session
    payload = optimize_payload(str(uuid4()))
    payload.update(change)
    response = client.post("/api/plans/optimize", json=payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_PLAN_DATA"


@pytest.mark.parametrize("invalid_kind", ["fixed", "overlap", "outside", "invented"])
def test_optimize_retries_then_rejects_unsafe_output(
    client_and_session,
    invalid_kind,
) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        add_schedule(
            db, user_id, time(12, 0), time(13, 0), schedule_type="FIXED"
        )
        db.commit()
    payload = optimize_payload(user_id)

    if invalid_kind == "fixed":
        output = optimize_output(start_time="12:00", end_time="13:00")
    elif invalid_kind == "outside":
        output = optimize_output(start_time="08:00", end_time="09:00")
    elif invalid_kind == "invented":
        output = optimize_output(title="입력하지 않은 일")
    else:
        payload["tasks"] = [
            *payload["tasks"],
            {
                "title": "운동",
                "estimated_minutes": 60,
                "priority": 2,
                "category": "건강",
            },
        ]
        output = optimize_output()
        output.optimized_schedules.append(
            OptimizedSchedule(
                title="운동",
                start_time="09:30",
                end_time="10:30",
                priority=2,
                schedule_type="ADJUSTABLE",
                category="건강",
                reason="몸을 움직일 시간입니다.",
            )
        )

    fake = FakeAIService(optimize_results=[output])
    use_fake_ai(fake)
    response = client.post("/api/plans/optimize", json=payload)

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "AI_INVALID_OUTPUT"
    assert fake.optimize_calls == 2


def test_optimize_returns_unscheduled_tasks_when_time_is_insufficient(
    client_and_session,
) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        db.commit()
    output = OptimizeAIOutput(
        summary="사용 가능한 시간이 부족합니다.",
        optimized_schedules=[],
        unscheduled_tasks=[
            UnscheduledTask(
                title="과제",
                estimated_minutes=60,
                reason="사용 가능한 시간이 부족합니다.",
            )
        ],
        advice="가능한 시간을 다시 확인해보세요.",
    )
    use_fake_ai(FakeAIService(optimize_results=[output]))

    response = client.post("/api/plans/optimize", json=optimize_payload(user_id))
    assert response.status_code == 200
    assert response.json()["data"]["unscheduled_tasks"][0]["title"] == "과제"


@pytest.mark.parametrize(
    ("error", "status_code", "error_code"),
    [
        (AIServiceTimeoutError(), 504, "AI_TIMEOUT"),
        (AIServiceError(), 502, "AI_SERVICE_ERROR"),
    ],
)
def test_optimize_maps_ai_errors(
    client_and_session,
    error,
    status_code,
    error_code,
) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        db.commit()
    use_fake_ai(FakeAIService(optimize_results=[error]))

    response = client.post("/api/plans/optimize", json=optimize_payload(user_id))
    assert response.status_code == status_code
    assert response.json()["error"]["code"] == error_code


def test_optimize_retries_transient_schema_error(client_and_session) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        db.commit()
    fake = FakeAIService(
        optimize_results=[AIOutputValidationError(), optimize_output()]
    )
    use_fake_ai(fake)

    response = client.post("/api/plans/optimize", json=optimize_payload(user_id))

    assert response.status_code == 200
    assert fake.optimize_calls == 2


def test_optimize_returns_503_without_api_key(client_and_session, monkeypatch) -> None:
    client, testing_session = client_and_session
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with testing_session() as db:
        user_id = add_user(db)
        db.commit()

    response = client.post("/api/plans/optimize", json=optimize_payload(user_id))
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "AI_NOT_CONFIGURED"
