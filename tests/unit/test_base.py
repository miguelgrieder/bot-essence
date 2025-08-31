from fastapi.testclient import TestClient

from bot_essence import main


def test_health_check_endpoint() -> None:

    with TestClient(app=main.app) as client:
        response = client.get("/health_check")

    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
