from fastapi.testclient import TestClient

from app.main import app


def test_login_and_read_published_knowledge():
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        login = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"})
        assert login.status_code == 200
        pages = client.get("/api/v1/pages")
        assert pages.status_code == 200
        assert pages.json()[0]["slug"] == "welcome"
