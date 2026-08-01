from collections.abc import Generator
from datetime import date, time
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
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


def valid_payload(user_id: str) -> dict[str, object]:
    return {
        "user_id": user_id,
        "date": "2026-08-02",
        "title": "프로젝트 보고서 작성",
        "start_time": "13:00",
        "end_time": "14:30",
        "priority": 3,
        "schedule_type": "ADJUSTABLE",
    }


def test_creates_schedule(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id = str(uuid4())
    with testing_session() as db:
        db.add(User(id=user_id, user_type="perfectionist"))
        db.commit()

    response = client.post("/api/schedules", json=valid_payload(user_id))

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"] == {
        "schedule_id": body["data"]["schedule_id"],
        "user_id": user_id,
        "date": "2026-08-02",
        "title": "프로젝트 보고서 작성",
        "start_time": "13:00",
        "end_time": "14:30",
        "priority": 3,
        "schedule_type": "ADJUSTABLE",
        "category": None,
        "is_completed": False,
        "satisfaction": None,
    }

    with testing_session() as db:
        saved_schedule = db.scalar(select(Schedule))
        assert saved_schedule is not None
        assert saved_schedule.id == body["data"]["schedule_id"]
        assert saved_schedule.created_at is not None
        assert saved_schedule.updated_at is not None


def test_returns_404_for_unknown_user(client_and_session) -> None:
    client, _ = client_and_session
    response = client.post("/api/schedules", json=valid_payload(str(uuid4())))

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


def test_rejects_invalid_time_range(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id = str(uuid4())
    with testing_session() as db:
        db.add(User(id=user_id, user_type="worry"))
        db.commit()
    payload = valid_payload(user_id)
    payload["start_time"] = "14:30"
    payload["end_time"] = "13:00"

    response = client.post("/api/schedules", json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_TIME_RANGE"


def test_rejects_invalid_priority(client_and_session) -> None:
    client, _ = client_and_session
    payload = valid_payload(str(uuid4()))
    payload["priority"] = 4

    response = client.post("/api/schedules", json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_SCHEDULE_DATA"


def add_schedule(
    db: Session,
    user_id: str,
    schedule_date: date,
    title: str,
    start_time: time,
    satisfaction: int | None = None,
) -> str:
    schedule_id = str(uuid4())
    db.add(
        Schedule(
            id=schedule_id,
            user_id=user_id,
            date=schedule_date,
            title=title,
            start_time=start_time,
            end_time=time(start_time.hour + 1, start_time.minute),
            priority=2,
            schedule_type="FIXED",
            category=None,
            is_completed=False,
            satisfaction=satisfaction,
        )
    )
    return schedule_id


def test_gets_only_matching_schedules_in_start_time_order(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id = str(uuid4())
    other_user_id = str(uuid4())
    with testing_session() as db:
        db.add_all(
            [
                User(id=user_id, user_type="perfectionist"),
                User(id=other_user_id, user_type="dopamine"),
            ]
        )
        db.flush()
        add_schedule(db, user_id, date(2026, 8, 2), "오후 일정", time(15, 0))
        add_schedule(db, user_id, date(2026, 8, 2), "오전 일정", time(9, 0))
        add_schedule(db, user_id, date(2026, 8, 3), "다른 날짜", time(8, 0))
        add_schedule(db, other_user_id, date(2026, 8, 2), "다른 사용자", time(7, 0))
        db.commit()

    response = client.get(
        "/api/schedules",
        params={"user_id": user_id, "date": "2026-08-02"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["date"] == "2026-08-02"
    assert [item["title"] for item in body["data"]["schedules"]] == [
        "오전 일정",
        "오후 일정",
    ]


def test_get_schedules_returns_empty_list(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id = str(uuid4())
    with testing_session() as db:
        db.add(User(id=user_id, user_type="overloaded"))
        db.commit()

    response = client.get(
        "/api/schedules",
        params={"user_id": user_id, "date": "2026-08-02"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"date": "2026-08-02", "schedules": []},
    }


def test_get_schedules_returns_404_for_unknown_user(client_and_session) -> None:
    client, _ = client_and_session
    response = client.get(
        "/api/schedules",
        params={"user_id": str(uuid4()), "date": "2026-08-02"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


def test_get_schedules_rejects_invalid_date(client_and_session) -> None:
    client, _ = client_and_session
    response = client.get(
        "/api/schedules",
        params={"user_id": str(uuid4()), "date": "2026-02-30"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_SCHEDULE_DATA"


def create_schedule_for_update(
    testing_session: sessionmaker[Session],
    *,
    satisfaction: int | None = None,
) -> tuple[str, str]:
    user_id = str(uuid4())
    with testing_session() as db:
        db.add(User(id=user_id, user_type="perfectionist"))
        db.flush()
        schedule_id = add_schedule(
            db,
            user_id,
            date(2026, 8, 2),
            "기존 일정",
            time(13, 0),
            satisfaction,
        )
        db.commit()
    return user_id, schedule_id


def test_updates_schedule(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_schedule_for_update(testing_session)
    with testing_session() as db:
        original_updated_at = db.get(Schedule, schedule_id).updated_at

    response = client.patch(
        f"/api/schedules/{schedule_id}",
        json={
            "user_id": user_id,
            "start_time": "14:00",
            "end_time": "15:30",
            "priority": 2,
            "is_completed": True,
            "satisfaction": 4,
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["start_time"] == "14:00"
    assert data["end_time"] == "15:30"
    assert data["priority"] == 2
    assert data["is_completed"] is True
    assert data["satisfaction"] == 4
    with testing_session() as db:
        assert db.get(Schedule, schedule_id).updated_at > original_updated_at


def test_updates_only_provided_fields(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_schedule_for_update(testing_session)

    response = client.patch(
        f"/api/schedules/{schedule_id}",
        json={"user_id": user_id, "title": "  변경된 제목  "},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "변경된 제목"
    assert data["start_time"] == "13:00"
    assert data["end_time"] == "14:00"
    assert data["priority"] == 2


def test_update_returns_404_for_missing_schedule(client_and_session) -> None:
    client, _ = client_and_session
    response = client.patch(
        f"/api/schedules/{uuid4()}",
        json={"user_id": str(uuid4()), "title": "변경"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SCHEDULE_NOT_FOUND"


def test_update_hides_other_users_schedule(client_and_session) -> None:
    client, testing_session = client_and_session
    _, schedule_id = create_schedule_for_update(testing_session)

    response = client.patch(
        f"/api/schedules/{schedule_id}",
        json={"user_id": str(uuid4()), "title": "변경"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SCHEDULE_NOT_FOUND"


def test_update_rejects_invalid_time_against_existing_time(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_schedule_for_update(testing_session)

    response = client.patch(
        f"/api/schedules/{schedule_id}",
        json={"user_id": user_id, "start_time": "14:00"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_TIME_RANGE"


def test_update_rejects_end_time_before_existing_start_time(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_schedule_for_update(testing_session)

    response = client.patch(
        f"/api/schedules/{schedule_id}",
        json={"user_id": user_id, "end_time": "12:30"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_TIME_RANGE"


def test_update_rejects_invalid_priority(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_schedule_for_update(testing_session)

    response = client.patch(
        f"/api/schedules/{schedule_id}",
        json={"user_id": user_id, "priority": 4},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_SCHEDULE_DATA"


def test_update_rejects_empty_update(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_schedule_for_update(testing_session)

    response = client.patch(
        f"/api/schedules/{schedule_id}",
        json={"user_id": user_id},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "NO_UPDATE_FIELDS"


def test_update_can_clear_satisfaction(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_schedule_for_update(testing_session, satisfaction=5)

    response = client.patch(
        f"/api/schedules/{schedule_id}",
        json={"user_id": user_id, "satisfaction": None},
    )

    assert response.status_code == 200
    assert response.json()["data"]["satisfaction"] is None
    with testing_session() as db:
        assert db.get(Schedule, schedule_id).satisfaction is None


def test_deletes_only_requested_schedule(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_schedule_for_update(testing_session)
    with testing_session() as db:
        other_schedule_id = add_schedule(
            db,
            user_id,
            date(2026, 8, 3),
            "유지할 일정",
            time(10, 0),
        )
        db.commit()

    response = client.delete(
        f"/api/schedules/{schedule_id}",
        params={"user_id": user_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "schedule_id": schedule_id,
            "message": "일정이 삭제되었습니다.",
        },
    }
    with testing_session() as db:
        assert db.get(Schedule, schedule_id) is None
        assert db.get(Schedule, other_schedule_id) is not None
        assert db.get(User, user_id) is not None


def test_delete_returns_404_for_missing_schedule(client_and_session) -> None:
    client, _ = client_and_session
    response = client.delete(
        f"/api/schedules/{uuid4()}",
        params={"user_id": str(uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SCHEDULE_NOT_FOUND"


def test_delete_hides_other_users_schedule(client_and_session) -> None:
    client, testing_session = client_and_session
    owner_id, schedule_id = create_schedule_for_update(testing_session)

    response = client.delete(
        f"/api/schedules/{schedule_id}",
        params={"user_id": str(uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SCHEDULE_NOT_FOUND"
    with testing_session() as db:
        assert db.get(Schedule, schedule_id) is not None
        assert db.get(User, owner_id) is not None


def test_delete_returns_404_when_repeated(client_and_session) -> None:
    client, testing_session = client_and_session
    user_id, schedule_id = create_schedule_for_update(testing_session)

    first_response = client.delete(
        f"/api/schedules/{schedule_id}",
        params={"user_id": user_id},
    )
    second_response = client.delete(
        f"/api/schedules/{schedule_id}",
        params={"user_id": user_id},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 404
    assert second_response.json()["error"]["code"] == "SCHEDULE_NOT_FOUND"
