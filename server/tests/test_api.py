import os
import tempfile
from pathlib import Path
from uuid import uuid4

TEST_DATABASE = Path(tempfile.gettempdir()) / f"one-wiki-test-{os.getpid()}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"

from fastapi.testclient import TestClient

from app.main import app, sanitize_content


def test_login_and_read_published_knowledge():
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        login = client.post("/api/v1/auth/login", json={"username": "系统管理员", "password": "ChangeMe123!"})
        assert login.status_code == 200
        assert login.json()["user"]["username"] == "系统管理员"
        pages = client.get("/api/v1/pages")
        assert pages.status_code == 200
        assert pages.json()[0]["slug"] == "welcome"


def test_legacy_email_login_still_works():
    with TestClient(app) as client:
        login = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"})
        assert login.status_code == 200


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


def test_registration_creates_read_only_user():
    with TestClient(app) as client:
        email = f"reader-{uuid4()}@example.com"
        register = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "ChangeMe123!", "display_name": "Reader User"},
        )
        assert register.status_code == 200
        user = register.json()["user"]
        assert user["can_edit"] is False
        assert "Readers" in [group["name"] for group in user["groups"]]

        created = client.post(
            "/api/v1/pages",
            json={"title": "Read only draft", "summary": "", "content": "No edit", "tags": []},
        )
        assert created.status_code == 403


def test_admin_can_grant_edit_permission_with_group():
    with TestClient(app) as client:
        email = f"editor-{uuid4()}@example.com"
        register = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "ChangeMe123!", "display_name": "Editor User"},
        )
        assert register.status_code == 200
        user_id = register.json()["user"]["id"]
        client.post("/api/v1/auth/logout")

        assert client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"}).status_code == 200
        group = client.post("/api/v1/admin/groups", json={"name": f"Editors {uuid4()}", "description": "", "can_edit": True})
        assert group.status_code == 200
        added = client.post(f"/api/v1/admin/groups/{group.json()['id']}/members", json={"user_id": user_id})
        assert added.status_code == 200
        client.post("/api/v1/auth/logout")

        login = client.post("/api/v1/auth/login", json={"email": email, "password": "ChangeMe123!"})
        assert login.status_code == 200
        assert login.json()["user"]["can_edit"] is True
        created = client.post(
            "/api/v1/pages",
            json={"title": f"Editable draft {uuid4()}", "summary": "", "content": "Can edit", "tags": []},
        )
        assert created.status_code == 200


def test_settings_center_respects_group_permissions():
    with TestClient(app) as client:
        email = f"settings-{uuid4()}@example.com"
        registered = client.post("/api/v1/auth/register", json={"email": email, "password": "ChangeMe123!", "display_name": "Settings Viewer"})
        user_id = registered.json()["user"]["id"]
        client.post("/api/v1/auth/logout")
        assert client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"}).status_code == 200
        group = client.post("/api/v1/admin/groups", json={"name": f"Settings {uuid4()}", "description": "", "permissions": ["settings.view"]})
        assert group.status_code == 200
        assert client.post(f"/api/v1/admin/groups/{group.json()['id']}/members", json={"user_id": user_id}).status_code == 200
        client.post("/api/v1/auth/logout")
        assert client.post("/api/v1/auth/login", json={"email": email, "password": "ChangeMe123!"}).status_code == 200
        assert client.get("/api/v1/admin/settings").status_code == 200
        assert client.get("/api/v1/admin/summary").status_code == 403
        assert client.put("/api/v1/admin/settings", json={"site_name": "Forbidden"}).status_code == 403


def test_statistics_permission_allows_summary_without_other_management_permissions():
    with TestClient(app) as client:
        email = f"statistics-{uuid4()}@example.com"
        registered = client.post("/api/v1/auth/register", json={"email": email, "password": "ChangeMe123!", "display_name": "Statistics Viewer"})
        user_id = registered.json()["user"]["id"]
        client.post("/api/v1/auth/logout")
        assert client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"}).status_code == 200
        group = client.post("/api/v1/admin/groups", json={"name": f"Statistics {uuid4()}", "description": "", "permissions": ["statistics.view"]})
        assert group.status_code == 200
        assert client.post(f"/api/v1/admin/groups/{group.json()['id']}/members", json={"user_id": user_id}).status_code == 200
        client.post("/api/v1/auth/logout")
        login = client.post("/api/v1/auth/login", json={"email": email, "password": "ChangeMe123!"})
        assert login.status_code == 200
        assert login.json()["user"]["can_access_settings"] is True
        summary = client.get("/api/v1/admin/summary")
        assert summary.status_code == 200
        assert {"pages", "published", "drafts", "users", "active_users", "groups", "topics", "files"} <= summary.json().keys()


def test_admin_can_create_update_and_deactivate_user():
    with TestClient(app) as client:
        assert client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"}).status_code == 200
        username = f"managed-{uuid4()}"
        created = client.post("/api/v1/admin/users", json={"username": username, "password": "ChangeMe123!", "role": "reader", "is_active": True})
        assert created.status_code == 200
        user = created.json()
        assert user["username"] == username
        assert client.post("/api/v1/auth/login", json={"username": username, "password": "ChangeMe123!"}).status_code == 200
        assert client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"}).status_code == 200
        updated = client.put(f"/api/v1/admin/users/{user['id']}", json={"username": username, "display_name": "Managed Editor", "role": "editor", "is_active": True})
        assert updated.status_code == 200
        assert updated.json()["role"] == "editor"
        assert client.delete(f"/api/v1/admin/users/{user['id']}").status_code == 200
        users = client.get("/api/v1/admin/users").json()
        assert next(item for item in users if item["id"] == user["id"])["is_active"] is False


def test_admin_can_permanently_delete_document():
    with TestClient(app) as client:
        assert client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "ChangeMe123!"}).status_code == 200
        created = client.post("/api/v1/pages", json={"title": f"Delete me {uuid4()}", "summary": "", "content": "temporary", "tags": []})
        assert created.status_code == 200
        page = created.json()
        assert client.delete(f"/api/v1/pages/{page['id']}").status_code == 200
        assert client.get(f"/api/v1/pages/id/{page['id']}").status_code == 404
