import os
import sys
from typing import Optional, List, Dict, Any

from fastapi import HTTPException

# 将 apps/server 根目录注入系统路径
SERVER_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SERVER_ROOT not in sys.path:
    sys.path.insert(0, SERVER_ROOT)

from mcp.server.mcpserver import MCPServer
from app.models.database import SessionLocal
from app.core.audit import record_audit_log
from app.services.agent_knowledge_service import AgentKnowledgeService

mcp = MCPServer("KnowledgeCenterMCP")


def _mcp_user(db):
    return AgentKnowledgeService.resolve_mcp_principal(
        db,
        username=os.getenv("MCP_AUTH_USER"),
        api_key=os.getenv("MCP_API_KEY"),
    )


def _http_error_payload(exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return {"error": detail.get("message", "请求失败"), "code": detail.get("code", "HTTP_ERROR")}
    return {"error": str(detail), "code": "HTTP_ERROR"}


def _with_db(handler):
    db = SessionLocal()
    try:
        return handler(db)
    except HTTPException as exc:
        return _http_error_payload(exc)
    finally:
        db.close()


@mcp.tool(
    name="search_knowledge",
    description="在企业知识中心中检索已发布知识，返回可引用切片，带严格权限过滤。"
)
def search_knowledge(query: str, space_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
    def run(db):
        user = _mcp_user(db)
        results = AgentKnowledgeService.search(db, user, query, space_id=space_id, limit=limit)
        record_audit_log(db, action="mcp_search_knowledge", resource="mcp_server", user_id=user.id, username=user.username, details={"query": query})
        return results

    result = _with_db(run)
    return result if isinstance(result, list) else [result]


@mcp.tool(
    name="get_knowledge",
    description="根据知识 ID 获取已发布知识的正文、版本号、标签与引用 URI。"
)
def get_knowledge(knowledge_id: int) -> Dict[str, Any]:
    def run(db):
        user = _mcp_user(db)
        payload = AgentKnowledgeService.get_knowledge(db, knowledge_id, user)
        record_audit_log(db, action="mcp_get_knowledge", resource=f"knowledge:{knowledge_id}", user_id=user.id, username=user.username)
        return payload

    return _with_db(run)


@mcp.tool(
    name="get_latest_knowledge",
    description="根据知识 ID 读取当前已发布版本快照正文，而不是未治理的草稿。"
)
def get_latest_knowledge(knowledge_id: int) -> Dict[str, Any]:
    def run(db):
        user = _mcp_user(db)
        payload = AgentKnowledgeService.get_latest_knowledge(db, knowledge_id, user)
        record_audit_log(db, action="mcp_get_latest_knowledge", resource=f"knowledge:{knowledge_id}", user_id=user.id, username=user.username)
        return payload

    return _with_db(run)


@mcp.tool(
    name="list_spaces",
    description="列出当前 MCP 身份有权访问的知识空间。"
)
def list_spaces() -> List[Dict[str, Any]]:
    def run(db):
        user = _mcp_user(db)
        spaces = AgentKnowledgeService.list_spaces(db, user)
        record_audit_log(db, action="mcp_list_spaces", resource="mcp_server", user_id=user.id, username=user.username)
        return spaces

    result = _with_db(run)
    return result if isinstance(result, list) else [result]


@mcp.tool(
    name="get_related_knowledge",
    description="获取同一空间内已发布且当前身份可见的关联知识（优先同专题/同标签）。"
)
def get_related_knowledge(knowledge_id: int) -> List[Dict[str, Any]]:
    def run(db):
        user = _mcp_user(db)
        related = AgentKnowledgeService.list_related(db, knowledge_id, user)
        record_audit_log(db, action="mcp_get_related", resource=f"knowledge:{knowledge_id}", user_id=user.id, username=user.username)
        return related

    result = _with_db(run)
    return result if isinstance(result, list) else [result]


@mcp.resource("knowledge://{knowledge_id}")
def read_knowledge_resource(knowledge_id: int) -> str:
    def run(db):
        user = _mcp_user(db)
        payload = AgentKnowledgeService.get_knowledge(db, knowledge_id, user)
        record_audit_log(db, action="mcp_read_resource", resource=f"knowledge:{knowledge_id}", user_id=user.id, username=user.username)
        return f"# {payload['title']}\n\n{payload['content']}"

    result = _with_db(run)
    if isinstance(result, dict) and result.get("error"):
        return f"无法读取知识: {result['error']}"
    return result


@mcp.resource("knowledge://space/{space_id}")
def read_space_resource(space_id: int) -> str:
    def run(db):
        user = _mcp_user(db)
        docs = AgentKnowledgeService.list_published_in_space(db, space_id, user)
        record_audit_log(db, action="mcp_read_space_resource", resource=f"space:{space_id}", user_id=user.id, username=user.username)
        lines = [f"- [#{d.id}] {d.title} ({AgentKnowledgeService.citation_uri(d.id)})" for d in docs]
        return "\n".join(lines) if lines else "该空间下暂无已发布知识"

    result = _with_db(run)
    if isinstance(result, dict) and result.get("error"):
        return f"无法读取空间: {result['error']}"
    return result


if __name__ == "__main__":
    mcp.run()
