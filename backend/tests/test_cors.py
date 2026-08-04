from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_vercel_origin_cors_preflight_is_allowed():
    """Vercel deployments can call the public backend from a browser."""
    origin = "https://redesignlife.vercel.app"

    response = client.options(
        "/api/users/type-test",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
