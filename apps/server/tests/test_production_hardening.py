from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.rate_limit import login_limiter
from app.main import app
from app.services.search_service import SearchService
from db_init import assert_not_production


client = TestClient(app)


def auth_headers(username: str, password: str):
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def test_user_list_requires_admin():
    client.post("/api/v1/auth/register", json={"username": "plain_viewer", "password": "password123"})
    viewer = auth_headers("plain_viewer", "password123")
    denied = client.get("/api/v1/users/", headers=viewer)
    assert denied.status_code == 403

    admin = auth_headers("admin_test", "password123")
    allowed = client.get("/api/v1/users/", headers=admin)
    assert allowed.status_code == 200
    assert any(u["username"] == "plain_viewer" for u in allowed.json()["data"])


def test_update_user_rejects_unknown_role():
    admin = auth_headers("admin_test", "password123")
    created = client.post(
        "/api/v1/users/",
        json={"username": "role_probe", "password": "password123", "role": "viewer"},
        headers=admin,
    ).json()["data"]["id"]
    response = client.put(f"/api/v1/users/{created}", json={"role": "superroot"}, headers=admin)
    assert response.status_code == 422


def test_register_requires_eight_char_password():
    response = client.post("/api/v1/auth/register", json={"username": "shortpwd", "password": "1234567"})
    assert response.status_code == 422


def test_html_attachment_is_downloaded_not_inlined():
    admin = auth_headers("admin_test", "password123")
    space_id = client.post("/api/v1/spaces/", json={"name": "xss-space", "visibility": "private"}, headers=admin).json()["data"]["id"]
    knowledge_id = client.post(
        "/api/v1/knowledge/",
        json={"space_id": space_id, "title": "xss", "content": "body"},
        headers=admin,
    ).json()["data"]["id"]
    uploaded = client.post(
        f"/api/v1/attachments/{knowledge_id}",
        files={"file": ("note.html", b"<script>alert(1)</script>", "text/html")},
        headers=admin,
    )
    assert uploaded.status_code == 200
    att_id = uploaded.json()["data"]["id"]
    downloaded = client.get(f"/api/v1/attachments/{att_id}/download", headers=admin)
    assert downloaded.status_code == 200
    assert downloaded.headers["content-type"].startswith("application/octet-stream")
    assert "attachment" in downloaded.headers.get("content-disposition", "")


def test_executable_attachment_is_rejected():
    admin = auth_headers("admin_test", "password123")
    space_id = client.post("/api/v1/spaces/", json={"name": "exe-space", "visibility": "private"}, headers=admin).json()["data"]["id"]
    knowledge_id = client.post(
        "/api/v1/knowledge/",
        json={"space_id": space_id, "title": "exe", "content": "body"},
        headers=admin,
    ).json()["data"]["id"]
    response = client.post(
        f"/api/v1/attachments/{knowledge_id}",
        files={"file": ("payload.exe", b"MZ", "application/octet-stream")},
        headers=admin,
    )
    assert response.status_code == 422


def test_system_settings_persist_and_limit_upload_size():
    admin = auth_headers("admin_test", "password123")
    saved = client.put(
        "/api/v1/system/settings",
        json={"max_upload_size_mb": 1, "allowed_extensions": [".txt", ".md"]},
        headers=admin,
    )
    assert saved.status_code == 200
    fetched = client.get("/api/v1/system/settings", headers=admin)
    assert fetched.json()["data"]["max_upload_size_mb"] == 1
    assert fetched.json()["data"]["allowed_extensions"] == [".txt", ".md"]
    assert fetched.json()["data"]["storage_path"] == settings.UPLOAD_DIR

    space_id = client.post("/api/v1/spaces/", json={"name": "size-space", "visibility": "private"}, headers=admin).json()["data"]["id"]
    knowledge_id = client.post(
        "/api/v1/knowledge/",
        json={"space_id": space_id, "title": "size", "content": "body"},
        headers=admin,
    ).json()["data"]["id"]
    too_big = client.post(
        f"/api/v1/attachments/{knowledge_id}",
        files={"file": ("big.txt", b"x" * (1024 * 1024 + 1), "text/plain")},
        headers=admin,
    )
    assert too_big.status_code == 413
    blocked_ext = client.post(
        f"/api/v1/attachments/{knowledge_id}",
        files={"file": ("pic.png", b"png", "image/png")},
        headers=admin,
    )
    assert blocked_ext.status_code == 422


def test_password_change_invalidates_old_token():
    admin = auth_headers("admin_test", "password123")
    created = client.post(
        "/api/v1/users/",
        json={"username": "stamp_user", "password": "oldpass12", "role": "viewer"},
        headers=admin,
    )
    assert created.status_code == 200
    old = auth_headers("stamp_user", "oldpass12")
    assert client.get("/api/v1/auth/me", headers=old).status_code == 200
    updated = client.put(
        f"/api/v1/users/{created.json()['data']['id']}",
        json={"password": "newpass12"},
        headers=admin,
    )
    assert updated.status_code == 200
    assert client.get("/api/v1/auth/me", headers=old).status_code == 401
    fresh = auth_headers("stamp_user", "newpass12")
    assert client.get("/api/v1/auth/me", headers=fresh).status_code == 200


def test_login_rate_limit_locks_after_failures(monkeypatch):
    monkeypatch.setattr(login_limiter, "_disabled", lambda: False)
    login_limiter.reset_all()
    for _ in range(8):
        response = client.post("/api/v1/auth/login", json={"username": "admin_test", "password": "wrong-password"})
        assert response.status_code == 401
    locked = client.post("/api/v1/auth/login", json={"username": "admin_test", "password": "wrong-password"})
    assert locked.status_code == 429
    still_locked = client.post("/api/v1/auth/login", json={"username": "admin_test", "password": "password123"})
    assert still_locked.status_code == 429
    login_limiter.reset_all()


def test_db_init_refuses_production():
    try:
        assert_not_production("production")
        assert False, "expected SystemExit"
    except SystemExit:
        pass
    assert_not_production("test")


def test_fulltext_query_strips_boolean_operators():
    assert SearchService._sanitize_fulltext('+foo -bar (baz)') == "foo  bar  baz"
