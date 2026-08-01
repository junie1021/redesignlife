from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from backend import main
from backend.database import Base, get_db
from backend.models import User


def test_create_test_result_and_tie_breaking() -> None:
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
                response = client.post(
                    "/api/test-result",
                    json={"answers": ["worry", "dopamine", "dopamine", "worry"]},
                )
                second_response = client.post(
                    "/api/test-result",
                    json={"answers": ["worry", "dopamine", "dopamine", "worry"]},
                )

            assert response.status_code == 201
            assert second_response.status_code == 201
            body = response.json()
            second_body = second_response.json()
            assert body["success"] is True
            assert body["data"]["user_type"] == "worry"
            assert body["data"]["user_id"] != second_body["data"]["user_id"]

            with Session(test_engine) as db:
                saved_users = list(db.scalars(select(User)))
                assert len(saved_users) == 2
                assert saved_users[0].id == body["data"]["user_id"]
                assert all(user.created_at is not None for user in saved_users)
        finally:
            main.app.dependency_overrides.clear()
            test_engine.dispose()


def test_rejects_invalid_answers() -> None:
    with TestClient(main.app) as client:
        response = client.post(
            "/api/test-result",
            json={"answers": ["perfectionist", "unknown"]},
        )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "error": {
            "code": "INVALID_TEST_ANSWERS",
            "message": "심리테스트 답변을 올바르게 입력해주세요.",
        },
    }
