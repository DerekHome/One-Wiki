import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.entities import ModuleConfig

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_full_business_flow(db_session):
    # 1. 注册并登录管理员
    reg_admin = client.post("/api/v1/auth/register", json={"username": "public_registration", "password": "password123", "role": "admin"})
    assert reg_admin.status_code == 422

    login_admin = client.post("/api/v1/auth/login", json={"username": "admin_test", "password": "password123"})
    assert login_admin.status_code == 200
    admin_token = login_admin.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. 注册普通用户 user_a (编辑者) 和 user_b (浏览者)
    client.post("/api/v1/auth/register", json={"username": "user_a", "password": "password123"})
    client.post("/api/v1/auth/register", json={"username": "user_b", "password": "password123"})
    
    login_a = client.post("/api/v1/auth/login", json={"username": "user_a", "password": "password123"}).json()["data"]
    login_b = client.post("/api/v1/auth/login", json={"username": "user_b", "password": "password123"}).json()["data"]
    headers_a = {"Authorization": f"Bearer {login_a['access_token']}"}
    headers_b = {"Authorization": f"Bearer {login_b['access_token']}"}

    # 3. 创建空间
    create_space = client.post("/api/v1/spaces/", json={"name": "研发知识库", "description": "核心研发文档", "visibility": "internal"}, headers=admin_headers)
    assert create_space.status_code == 200
    space_id = create_space.json()["data"]["id"]

    # 4. 给 user_a 分配 editor 权限，给 user_b 分配 viewer 权限
    client.post(f"/api/v1/spaces/{space_id}/members", json={"user_id": login_a["user"]["id"], "role": "editor"}, headers=admin_headers)
    client.post(f"/api/v1/spaces/{space_id}/members", json={"user_id": login_b["user"]["id"], "role": "viewer"}, headers=admin_headers)

    # 5. user_a 创建知识并自动生成 Version 1
    create_k = client.post("/api/v1/knowledge/", json={
        "space_id": space_id,
        "title": "FastAPI高并发微内核架构设计",
        "content": "# 核心设计\n本文介绍微内核架构的设计原则与实践指南。",
        "summary": "微内核核心架构",
        "tags": ["后端架构", "FastAPI"]
    }, headers=headers_a)
    assert create_k.status_code == 200
    k_id = create_k.json()["data"]["id"]
    assert create_k.json()["data"]["current_version_id"] is not None

    # 6. user_a 修改知识并生成 Version 2
    update_k = client.put(f"/api/v1/knowledge/{k_id}", json={
        "title": "FastAPI高并发微内核架构设计(v2修订版)",
        "content": "# 核心设计\n本文介绍微内核架构的设计原则与实践指南。\n新增事件总线与插件机制章节。",
        "change_summary": "增加事件总线章节"
    }, headers=headers_a)
    assert update_k.status_code == 200
    assert update_k.json()["data"]["title"] == "FastAPI高并发微内核架构设计(v2修订版)"

    # 7. 查看版本历史与差异比较
    versions = client.get(f"/api/v1/knowledge/{k_id}/versions", headers=headers_b)
    assert versions.status_code == 200
    assert len(versions.json()["data"]) >= 2

    diff = client.get(f"/api/v1/knowledge/{k_id}/diff?v_from=1&v_to=2", headers=headers_b)
    assert diff.status_code == 200
    assert "version_from" in diff.json()["data"]

    # 8. 恢复历史版本
    restore = client.post(f"/api/v1/knowledge/{k_id}/restore/1", headers=headers_a)
    assert restore.status_code == 200
    assert restore.json()["data"]["title"] == "FastAPI高并发微内核架构设计"

    # 9. user_b (仅 viewer) 尝试编辑，验证权限拦截 (应为 403)
    edit_by_b = client.put(f"/api/v1/knowledge/{k_id}", json={"title": "越权篡改"}, headers=headers_b)
    assert edit_by_b.status_code == 403

    # 10. 全文检索验证
    search_res = client.get("/api/v1/search/?q=微内核", headers=headers_b)
    assert search_res.status_code == 200
    assert len(search_res.json()["data"]["items"]) >= 1

    # 11. 标签与审计日志验证
    tags = client.get("/api/v1/tags/", headers=headers_b)
    assert tags.status_code == 200
    assert any(t["name"] == "后端架构" for t in tags.json()["data"])

    audit_logs = client.get("/api/v1/audit/", headers=admin_headers)
    assert audit_logs.status_code == 200
    assert audit_logs.json()["data"]["total"] > 0

    # 12. 模块停用与启用验证：禁用搜索模块后检索返回空，但知识 CRUD 依然正常
    disable_mod = client.post("/api/v1/modules/search/disable", headers=admin_headers)
    assert disable_mod.status_code == 200
    search_disabled = client.get("/api/v1/search/?q=微内核", headers=headers_b)
    assert len(search_disabled.json()["data"]["items"]) == 0
    persisted = db_session.query(ModuleConfig).filter(ModuleConfig.module_id == "search").one()
    assert persisted.status == "disabled"

    # 确认知识 CRUD 依然完好
    k_still_works = client.get(f"/api/v1/knowledge/{k_id}", headers=headers_b)
    assert k_still_works.status_code == 200

    # 重新启用搜索模块
    client.post("/api/v1/modules/search/enable", headers=admin_headers)
    db_session.expire_all()
    restored_row = db_session.query(ModuleConfig).filter(ModuleConfig.module_id == "search").one()
    assert restored_row.status == "enabled"
    search_restored = client.get("/api/v1/search/?q=微内核", headers=headers_b)
    assert len(search_restored.json()["data"]["items"]) >= 1

    # 13. Agent 开放接口验证
    agent_k = client.get(f"/api/v1/agent/knowledge/{k_id}/latest", headers=headers_b)
    assert agent_k.status_code == 200
    assert "knowledge_id" in agent_k.json()["data"]

    # 无 Token 访问 Agent 接口应被 401 拦截
    agent_no_auth = client.get(f"/api/v1/agent/knowledge/{k_id}/latest")
    assert agent_no_auth.status_code == 401

    print("ALL 13 BACKEND INTEGRATION TEST SUITES PASSED PERFECTLY!")

if __name__ == "__main__":
    test_health_check()
    test_full_business_flow()
