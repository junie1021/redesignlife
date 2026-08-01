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


def add_user(db: Session) -> str:
    user_id = str(uuid4())
    db.add(User(id=user_id, user_type="perfectionist"))
    return user_id


def add_schedule(
    db: Session,
    user_id: str,
    start_time: time,
    end_time: time,
    *,
    schedule_date: date = date(2026, 8, 2),
    title: str = "기존 일정",
    schedule_type: str = "FIXED",
) -> str:
    schedule_id = str(uuid4())
    db.add(
        Schedule(
            id=schedule_id,
            user_id=user_id,
            date=schedule_date,
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


def conflict_payload(
    user_id: str,
    start_time: str,
    end_time: str,
    *,
    exclude_schedule_id: str | None = None,
) -> dict[str, object]:
    return {
        "user_id": user_id,
        "date": "2026-08-02",
        "start_time": start_time,
        "end_time": end_time,
        "exclude_schedule_id": exclude_schedule_id,
    }


def create_user_with_schedule(
    testing_session: sessionmaker[Session],
    start_time: time = time(13, 0),
    end_time: time = time(14, 0),
) -> tuple[str, str]:
    with testing_session() as db:
        user_id = add_user(db)
        schedule_id = add_schedule(db, user_id, start_time, end_time)
        db.commit()
    return user_id, schedule_id


def test_returns_no_conflict_without_overlap_and_does_not_modify_db(
    client_and_session,
) -> None:
    client, testing_session = client_and_session
    user_id, _ = create_user_with_schedule(testing_session)

    response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(user_id, "15:00", "16:00"),
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "has_conflict": False,
        "conflict_count": 0,
        "conflicts": [],
    }
    with testing_session() as db:
        assert db.scalar(select(func.count()).select_from(Schedule)) == 1


@pytest.mark.parametrize(
    ("start_time", "end_time"),
    [
        ("13:30", "15:00"),
        ("12:00", "15:00"),
        ("13:15", "13:45"),
    ],
    ids=["partial-overlap", "new-contains-existing", "new-inside-existing"],
)
def test_detects_overlap_types(client_and_session, start_time, end_time) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_user_with_schedule(testing_session)

    response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(user_id, start_time, end_time),
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["has_conflict"] is True
    assert data["conflict_count"] == 1
    assert data["conflicts"][0]["schedule_id"] == schedule_id


def test_touching_time_ranges_do_not_conflict(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, _ = create_user_with_schedule(testing_session)

    response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(user_id, "14:00", "15:00"),
    )

    assert response.status_code == 200
    assert response.json()["data"]["has_conflict"] is False


def test_returns_multiple_conflicts_in_start_time_order(client_and_session) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        later_id = add_schedule(
            db,
            user_id,
            time(14, 30),
            time(16, 0),
            title="보고서 작성",
            schedule_type="ADJUSTABLE",
        )
        earlier_id = add_schedule(
            db, user_id, time(13, 0), time(14, 0), title="팀 회의"
        )
        db.commit()

    response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(user_id, "13:30", "15:00"),
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["conflict_count"] == 2
    assert [conflict["schedule_id"] for conflict in data["conflicts"]] == [
        earlier_id,
        later_id,
    ]


def test_ignores_schedule_on_another_date(client_and_session) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        add_schedule(
            db,
            user_id,
            time(13, 0),
            time(14, 0),
            schedule_date=date(2026, 8, 3),
        )
        db.commit()

    response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(user_id, "13:30", "14:30"),
    )

    assert response.status_code == 200
    assert response.json()["data"]["has_conflict"] is False


def test_ignores_other_users_schedule_and_foreign_exclusion(client_and_session) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        other_user_id = add_user(db)
        other_schedule_id = add_schedule(
            db, other_user_id, time(13, 0), time(14, 0)
        )
        db.commit()

    response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(
            user_id,
            "13:30",
            "14:30",
            exclude_schedule_id=other_schedule_id,
        ),
    )

    assert response.status_code == 200
    assert response.json()["data"]["has_conflict"] is False


def test_excludes_requested_schedule_and_tolerates_unknown_id(
    client_and_session,
) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_user_with_schedule(testing_session)

    excluded_response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(
            user_id,
            "13:30",
            "14:30",
            exclude_schedule_id=schedule_id,
        ),
    )
    unknown_response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(
            user_id,
            "13:30",
            "14:30",
            exclude_schedule_id=str(uuid4()),
        ),
    )

    assert excluded_response.status_code == 200
    assert excluded_response.json()["data"]["has_conflict"] is False
    assert unknown_response.status_code == 200
    assert unknown_response.json()["data"]["has_conflict"] is True


def test_conflict_check_returns_404_for_unknown_user(client_and_session) -> None:
    client, _ = client_and_session
    response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(str(uuid4()), "13:00", "14:00"),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


@pytest.mark.parametrize(
    ("start_time", "end_time"),
    [("13:00", "13:00"), ("14:00", "13:00")],
)
def test_conflict_check_rejects_invalid_time_range(
    client_and_session,
    start_time,
    end_time,
) -> None:
    client, testing_session = client_and_session
    with testing_session() as db:
        user_id = add_user(db)
        db.commit()

    response = client.post(
        "/api/schedules/check-conflicts",
        json=conflict_payload(user_id, start_time, end_time),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_TIME_RANGE"


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("date", "2026-02-30"),
        ("start_time", "13:00:00"),
        ("end_time", "25:00"),
    ],
)
def test_conflict_check_rejects_invalid_formats(
    client_and_session,
    field_name,
    invalid_value,
) -> None:
    client, _ = client_and_session
    payload = conflict_payload(str(uuid4()), "13:00", "14:00")
    payload[field_name] = invalid_value

    response = client.post("/api/schedules/check-conflicts", json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_SCHEDULE_DATA"
