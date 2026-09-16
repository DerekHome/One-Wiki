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
