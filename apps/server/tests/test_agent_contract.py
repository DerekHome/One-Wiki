from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.modules.registry import module_registry
from app.main import app
from app.models.entities import Knowledge
from app.services.agent_knowledge_service import AgentKnowledgeService


client = TestClient(app)


def auth_headers(username: str, password: str):
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _seed_published(admin, title="agent-doc", content="published body", tags=None):
    space_id = client.post(
        "/api/v1/spaces/",
        json={"name": f"space-{title}", "visibility": "private"},
        headers=admin,
    ).json()["data"]["id"]
    knowledge = client.post(
        "/api/v1/knowledge/",
        json={"space_id": space_id, "title": title, "content": content, "tags": tags or ["规范"]},
        headers=admin,
    ).json()["data"]
    return space_id, knowledge["id"]


def test_agent_latest_returns_version_snapshot_and_citation(db_session):
    module_registry.enable("search")
    admin = auth_headers("admin_test", "password123")
    space_id, knowledge_id = _seed_published(admin, title="versioned", content="v1 body")
    client.put(
        f"/api/v1/knowledge/{knowledge_id}",
        json={"content": "v2 published body", "change_summary": "publish v2"},
        headers=admin,
    )

    row = db_session.get(Knowledge, knowledge_id)
    row.content = "stale-row-content"
    db_session.commit()

    latest = client.get(f"/api/v1/agent/knowledge/{knowledge_id}/latest", headers=admin)
    assert latest.status_code == 200
    data = latest.json()["data"]
    assert data["content"] == "v2 published body"
    assert data["version_number"] == 2
    assert data["version"] == 2
    assert data["citation_uri"] == f"knowledge://{knowledge_id}"
    assert data["space_id"] == space_id
    assert "规范" in data["tags"]
    assert "stale-row-content" not in data["content"]


def test_agent_hides_unpublished_knowledge(db_session):
    admin = auth_headers("admin_test", "password123")
    _, knowledge_id = _seed_published(admin, title="draft-hidden", content="should not leak")

    row = db_session.get(Knowledge, knowledge_id)
    row.status = "draft"
    db_session.commit()

    agent = client.get(f"/api/v1/agent/knowledge/{knowledge_id}", headers=admin)
    assert agent.status_code == 404
    human = client.get(f"/api/v1/knowledge/{knowledge_id}", headers=admin)
    assert human.status_code == 200


def test_agent_related_skips_unpublished(db_session):
    admin = auth_headers("admin_test", "password123")
    space_id, knowledge_id = _seed_published(admin, title="related-src", content="src")
    other_id = client.post(
        "/api/v1/knowledge/",
        json={"space_id": space_id, "title": "related-published", "content": "ok", "tags": ["规范"]},
        headers=admin,
    ).json()["data"]["id"]
    hidden_id = client.post(
        "/api/v1/knowledge/",
        json={"space_id": space_id, "title": "related-draft", "content": "secret", "tags": ["规范"]},
        headers=admin,
    ).json()["data"]["id"]

    row = db_session.get(Knowledge, hidden_id)
    row.status = "draft"
    db_session.commit()

    related = client.get(f"/api/v1/agent/related/{knowledge_id}", headers=admin).json()["data"]
    ids = [item["knowledge_id"] for item in related]
    assert other_id in ids
    assert hidden_id not in ids
    assert all(item["citation_uri"].startswith("knowledge://") for item in related)


def test_agent_search_disabled_is_explicit():
    admin = auth_headers("admin_test", "password123")
    module_registry.disable("search")
    try:
        response = client.get("/api/v1/agent/search?q=anything", headers=admin)
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "SEARCH_MODULE_DISABLED"
    finally:
        module_registry.enable("search")


def test_mcp_identity_refuses_admin_fallback(db_session):
    missing = None
    try:
        AgentKnowledgeService.resolve_mcp_user(db_session, "")
    except HTTPException as exc:
        missing = exc
    assert missing is not None and missing.status_code == 401
    assert missing.detail["code"] == "MCP_AUTH_REQUIRED"

    invalid = None
    try:
        AgentKnowledgeService.resolve_mcp_user(db_session, "ghost-agent")
    except HTTPException as exc:
        invalid = exc
    assert invalid is not None and invalid.status_code == 401

    user = AgentKnowledgeService.resolve_mcp_user(db_session, "admin_test")
    assert user.username == "admin_test"


def test_draft_is_hidden_until_published():
    admin = auth_headers("admin_test", "password123")
    space_id = client.post("/api/v1/spaces/", json={"name": "draft-space", "visibility": "private"}, headers=admin).json()["data"]["id"]
    created = client.post("/api/v1/knowledge/", json={
        "space_id": space_id,
        "title": "draft-doc",
        "content": "not for agents yet",
        "status": "draft",
    }, headers=admin)
    assert created.status_code == 200
    knowledge_id = created.json()["data"]["id"]
    assert created.json()["data"]["status"] == "draft"

    listed = client.get(f"/api/v1/knowledge/?space_id={space_id}", headers=admin).json()["data"]
    assert any(item["id"] == knowledge_id for item in listed)

    hidden = client.get(f"/api/v1/agent/knowledge/{knowledge_id}/latest", headers=admin)
    assert hidden.status_code == 404

    published = client.put(f"/api/v1/knowledge/{knowledge_id}", json={"status": "published"}, headers=admin)
    assert published.status_code == 200
    visible = client.get(f"/api/v1/agent/knowledge/{knowledge_id}/latest", headers=admin)
    assert visible.status_code == 200
    assert visible.json()["data"]["citation_uri"] == f"knowledge://{knowledge_id}"


def test_agent_api_key_is_read_only_and_space_scoped():
    admin = auth_headers("admin_test", "password123")
    space_a, knowledge_a = _seed_published(admin, title="key-space-a", content="alpha")
    space_b, knowledge_b = _seed_published(admin, title="key-space-b", content="beta")

    created = client.post("/api/v1/agent-keys/", json={"name": "bot-a", "space_id": space_a}, headers=admin)
    assert created.status_code == 200
    raw_key = created.json()["data"]["api_key"]
    assert raw_key.startswith("kck_")
    agent_headers = {"Authorization": f"Bearer {raw_key}"}

    allowed = client.get(f"/api/v1/agent/knowledge/{knowledge_a}/latest", headers=agent_headers)
    assert allowed.status_code == 200
    denied = client.get(f"/api/v1/agent/knowledge/{knowledge_b}/latest", headers=agent_headers)
    assert denied.status_code == 403

    write_blocked = client.post("/api/v1/knowledge/", json={
        "space_id": space_a,
        "title": "agent-write",
        "content": "should fail",
    }, headers=agent_headers)
    assert write_blocked.status_code == 403
    assert write_blocked.json()["error"]["code"] == "AGENT_READ_ONLY"

    topics = client.get(f"/api/v1/agent/spaces/{space_a}/topics", headers=agent_headers)
    assert topics.status_code == 200
    attachments = client.get(f"/api/v1/agent/knowledge/{knowledge_a}/attachments", headers=agent_headers)
    assert attachments.status_code == 200


def test_mcp_prefers_api_key_identity(db_session):
    admin = auth_headers("admin_test", "password123")
    created = client.post("/api/v1/agent-keys/", json={"name": "mcp-bot"}, headers=admin).json()["data"]
    user = AgentKnowledgeService.resolve_mcp_principal(db_session, username="ignored", api_key=created["api_key"])
    assert user.actor_type == "agent"
    assert user.agent_key_name == "mcp-bot"


def test_non_admin_can_issue_agent_key():
    client.post("/api/v1/auth/register", json={"username": "key_editor", "password": "password123"})
    login = client.post("/api/v1/auth/login", json={"username": "key_editor", "password": "password123"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    created = client.post("/api/v1/agent-keys/", json={"name": "my-bot"}, headers=headers)
    assert created.status_code == 200
    assert created.json()["data"]["api_key"].startswith("kck_")

    listed = client.get("/api/v1/agent-keys/", headers=headers)
    assert listed.status_code == 200
    assert any(item["name"] == "my-bot" for item in listed.json()["data"])


def test_mcp_fastmcp_server_loads():
    from app.mcp_server import mcp

    assert mcp.name == "KnowledgeCenterMCP"


def test_agent_key_profile_permissions_and_multi_space():
    module_registry.enable("search")
    admin = auth_headers("admin_test", "password123")
    space_a, knowledge_a = _seed_published(admin, title="perm-a", content="alpha body")
    space_b, knowledge_b = _seed_published(admin, title="perm-b", content="beta body")
    space_c, knowledge_c = _seed_published(admin, title="perm-c", content="gamma body")

    created = client.post("/api/v1/agent-keys/", json={
        "name": "scoped-bot",
        "description": "客服只读助手",
        "space_ids": [space_a, space_b],
        "permissions": ["read", "list_spaces"],
    }, headers=admin)
    assert created.status_code == 200
    data = created.json()["data"]
    assert data["description"] == "客服只读助手"
    assert set(data["space_ids"]) == {space_a, space_b}
    assert "search" not in data["permissions"]
    agent = {"Authorization": f"Bearer {data['api_key']}"}

    assert client.get(f"/api/v1/agent/knowledge/{knowledge_a}/latest", headers=agent).status_code == 200
    assert client.get(f"/api/v1/agent/knowledge/{knowledge_b}/latest", headers=agent).status_code == 200
    assert client.get(f"/api/v1/agent/knowledge/{knowledge_c}/latest", headers=agent).status_code == 403

    search_denied = client.get("/api/v1/agent/search?q=alpha", headers=agent)
    assert search_denied.status_code == 403
    assert search_denied.json()["error"]["code"] == "AGENT_PERMISSION_DENIED"

    updated = client.put(f"/api/v1/agent-keys/{data['id']}", json={
        "description": "缩小范围后开放检索",
        "space_ids": [space_a],
        "permissions": ["read", "search", "list_spaces"],
    }, headers=admin)
    assert updated.status_code == 200
    assert updated.json()["data"]["description"] == "缩小范围后开放检索"
    assert updated.json()["data"]["space_ids"] == [space_a]

    search_ok = client.get("/api/v1/agent/search?q=alpha", headers=agent)
    assert search_ok.status_code == 200
    assert client.get(f"/api/v1/agent/knowledge/{knowledge_b}/latest", headers=agent).status_code == 403


def test_non_admin_can_update_own_agent_profile():
    client.post("/api/v1/auth/register", json={"username": "profile_editor", "password": "password123"})
    login = client.post("/api/v1/auth/login", json={"username": "profile_editor", "password": "password123"})
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    created = client.post("/api/v1/agent-keys/", json={"name": "desk-bot"}, headers=headers)
    assert created.status_code == 200
    key_id = created.json()["data"]["id"]

    updated = client.put(f"/api/v1/agent-keys/{key_id}", json={
        "description": "内部助手",
        "permissions": ["read", "search"],
    }, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["data"]["description"] == "内部助手"
    assert set(updated.json()["data"]["permissions"]) == {"read", "search"}
