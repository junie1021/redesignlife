from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_api_index_lists_public_endpoints() -> None:
    """The API root exposes the documented backend routes."""
    response = client.get("/api/")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "docs": "/docs",
            "health": "/health",
            "endpoints": [
                "POST /api/users/type-test",
                "POST /api/schedules",
                "GET /api/days/{date}/tasks",
                "GET /api/schedules/range",
                "POST /api/schedules/check-conflicts",
                "PATCH /api/schedules/{schedule_id}",
                "DELETE /api/schedules/{schedule_id}",
                "GET /api/daily-summary",
                "POST /api/days/{date}/recovery",
                "POST /api/plans/optimize",
            ],
        },
    }


def test_api_index_is_available_without_trailing_slash() -> None:
    """The API root works with either URL form without redirecting."""
    response = client.get("/api", follow_redirects=False)

    assert response.status_code == 200
