from collections.abc import Generator
from datetime import date, time
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend import main
from backend.database import Base, get_db
from backend.models import Schedule, User


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


def add_summary_schedule(
    db: Session,
    user_id: str,
    start_time: time,
    end_time: time,
    schedule_type: str,
    is_completed: bool,
    satisfaction: int | None,
    schedule_date: date = date(2026, 8, 2),
) -> None:
    db.add(
        Schedule(
            id=str(uuid4()),
            user_id=user_id,
            date=schedule_date,
            title="통계 일정",
            start_time=start_time,
            end_time=end_time,
            priority=2,
            schedule_type=schedule_type,
            category=None,
            is_completed=is_completed,
            satisfaction=satisfaction,
        )
    )


def test_returns_daily_summary(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id = str(uuid4())
    other_user_id = str(uuid4())
    with testing_session() as db:
        db.add_all(
            [
                User(id=user_id, user_type="perfectionist"),
                User(id=other_user_id, user_type="worry"),
            ]
        )
        db.flush()
        add_summary_schedule(db, user_id, time(9, 0), time(10, 30), "FIXED", True, 4)
        add_summary_schedule(
            db, user_id, time(11, 0), time(12, 0), "ADJUSTABLE", True, 5
        )
        add_summary_schedule(
            db, user_id, time(14, 0), time(15, 30), "ADJUSTABLE", False, None
        )
        add_summary_schedule(
            db, other_user_id, time(8, 0), time(9, 0), "FIXED", True, 1
        )
        add_summary_schedule(
            db,
            user_id,
            time(8, 0),
            time(9, 0),
            "FIXED",
            True,
            1,
            date(2026, 8, 3),
        )
        db.commit()

    response = client.get(
        "/api/daily-summary",
        params={"user_id": user_id, "date": "2026-08-02"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "user_id": user_id,
            "user_type": "perfectionist",
            "date": "2026-08-02",
            "total_count": 3,
            "completed_count": 2,
            "incomplete_count": 1,
            "completion_rate": 66.67,
            "average_satisfaction": 4.5,
            "fixed_count": 1,
            "adjustable_count": 2,
            "total_planned_minutes": 240,
            "completed_planned_minutes": 150,
        },
    }


def test_returns_zero_summary_without_schedules(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id = str(uuid4())
    with testing_session() as db:
        db.add(User(id=user_id, user_type="worry"))
        db.commit()

    response = client.get(
        "/api/daily-summary",
        params={"user_id": user_id, "date": "2026-08-02"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_count"] == 0
    assert data["completed_count"] == 0
    assert data["incomplete_count"] == 0
    assert data["completion_rate"] == 0.0
    assert data["average_satisfaction"] is None
    assert data["total_planned_minutes"] == 0
    assert data["completed_planned_minutes"] == 0


def test_returns_null_average_without_satisfaction(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id = str(uuid4())
    with testing_session() as db:
        db.add(User(id=user_id, user_type="dopamine"))
        db.flush()
        add_summary_schedule(
            db, user_id, time(9, 0), time(10, 0), "FIXED", False, None
        )
        db.commit()

    response = client.get(
        "/api/daily-summary",
        params={"user_id": user_id, "date": "2026-08-02"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["average_satisfaction"] is None


def test_daily_summary_returns_404_for_unknown_user(client_and_session) -> None:
    client, _ = client_and_session
    response = client.get(
        "/api/daily-summary",
        params={"user_id": str(uuid4()), "date": "2026-08-02"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


def test_daily_summary_rejects_invalid_date(client_and_session) -> None:
    client, _ = client_and_session
    response = client.get(
        "/api/daily-summary",
        params={"user_id": str(uuid4()), "date": "2026-02-30"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_SCHEDULE_DATA"
