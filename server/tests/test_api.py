from fastapi.testclient import TestClient

from app.main import app, sanitize_content


def test_login_and_read_published_knowledge():
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        login = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"})
        assert login.status_code == 200
        pages = client.get("/api/v1/pages")
        assert pages.status_code == 200
        assert pages.json()[0]["slug"] == "welcome"


def test_user_can_favorite_and_list_published_knowledge():
    with TestClient(app) as client:
        login = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"})
        assert login.status_code == 200
        page = client.get("/api/v1/pages").json()[0]
        favorite = client.post(f"/api/v1/pages/{page['id']}/favorite")
        assert favorite.status_code == 200
        active = favorite.json()["active"]
        favorites = client.get("/api/v1/favorites")
        assert favorites.status_code == 200
        assert (page["id"] in [item["id"] for item in favorites.json()]) is active
        restored = client.post(f"/api/v1/pages/{page['id']}/favorite")
        assert restored.json()["active"] is not active


def test_page_content_is_sanitized_before_storage():
    assert sanitize_content("<p>可信内容</p><script>alert('xss')</script>") == "<p>可信内容</p>alert('xss')"


def test_user_can_list_page_attachments():
    with TestClient(app) as client:
        login = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"})
        assert login.status_code == 200
        page = client.get("/api/v1/pages").json()[0]
        files = client.get(f"/api/v1/pages/{page['id']}/files")
        assert files.status_code == 200
        assert files.json() == []
