from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def auth_headers(username: str, password: str):
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def test_public_registration_cannot_grant_admin():
    response = client.post("/api/v1/auth/register", json={
        "username": "public_security_probe",
        "password": "strong-password",
        "role": "admin",
    })
    assert response.status_code == 422


def test_topic_delete_requires_topic_to_belong_to_path_space():
    admin = auth_headers("admin_test", "password123")
    victim_space = client.post("/api/v1/spaces/", json={"name": "victim-space", "visibility": "private"}, headers=admin).json()["data"]["id"]
    other_space = client.post("/api/v1/spaces/", json={"name": "other-space", "visibility": "private"}, headers=admin).json()["data"]["id"]
    topic = client.post(f"/api/v1/spaces/{victim_space}/topics", json={"name": "protected-topic"}, headers=admin).json()["data"]["id"]

    response = client.delete(f"/api/v1/spaces/{other_space}/topics/{topic}", headers=admin)
    assert response.status_code == 404
    remaining = client.get(f"/api/v1/spaces/{victim_space}/topics", headers=admin)
    assert any(item["id"] == topic for item in remaining.json()["data"])


def test_duplicate_attachment_names_are_independent():
    admin = auth_headers("admin_test", "password123")
    space_id = client.post("/api/v1/spaces/", json={"name": "attachment-space", "visibility": "private"}, headers=admin).json()["data"]["id"]
    knowledge_id = client.post("/api/v1/knowledge/", json={"space_id": space_id, "title": "attachments", "content": "content"}, headers=admin).json()["data"]["id"]

    first = client.post(f"/api/v1/attachments/{knowledge_id}", files={"file": ("same.txt", b"first", "text/plain")}, headers=admin).json()["data"]["id"]
    second = client.post(f"/api/v1/attachments/{knowledge_id}", files={"file": ("same.txt", b"second", "text/plain")}, headers=admin).json()["data"]["id"]
    assert first != second
    assert client.get(f"/api/v1/attachments/{first}/download", headers=admin).content == b"first"
    assert client.get(f"/api/v1/attachments/{second}/download", headers=admin).content == b"second"

    assert client.delete(f"/api/v1/attachments/{first}", headers=admin).status_code == 200
    assert client.get(f"/api/v1/attachments/{second}/download", headers=admin).content == b"second"
