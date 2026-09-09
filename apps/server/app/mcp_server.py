import os
import sys
import asyncio
from typing import Optional, List, Dict, Any

# 将 apps/server 根目录注入系统路径
SERVER_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SERVER_ROOT not in sys.path:
    sys.path.insert(0, SERVER_ROOT)

from mcp.server.mcpserver import MCPServer
from app.models.database import SessionLocal
from app.models.entities import User
from app.services.knowledge_service import KnowledgeService
from app.services.search_service import SearchService
from app.services.space_service import SpaceService
from app.core.audit import record_audit_log

# 初始化标准 MCP Server (v2 SDK)
mcp = MCPServer("KnowledgeCenterMCP")

def get_mcp_context_user(db):
    # 本地模式默认使用指定管理员或首个活跃管理员身份进行安全鉴权
    target_username = os.getenv("MCP_AUTH_USER", "admin_master")
    user = db.query(User).filter(User.username == target_username).first()
    if not user:
        user = db.query(User).filter(User.role.in_(["owner", "admin"])).first()
    if not user:
        user = db.query(User).first()
    return user

# ==================== MCP Tools 开放工具定义 ====================

@mcp.tool(
    name="search_knowledge",
    description="在企业知识中心中执行全文联合检索，检索标题、正文及摘要高亮切片，带严格权限过滤。"
)
def search_knowledge(query: str, space_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        user = get_mcp_context_user(db)
        if not user:
            return [{"error": "未找到有效 MCP 执行身份"}]
        results = SearchService.search(
            db=db,
            query_str=query,
            user=user,
            space_id=space_id,
            page=1,
            page_size=limit
        )
        record_audit_log(db, action="mcp_search_knowledge", resource="mcp_server", user_id=user.id, username=user.username, details={"query": query})
        return results.get("items", [])
    finally:
        db.close()

@mcp.tool(
    name="get_knowledge",
    description="根据知识 ID 获取指定知识对象的详细信息、元数据及正文内容。"
)
def get_knowledge(knowledge_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        user = get_mcp_context_user(db)
        k = KnowledgeService.get_knowledge(db, knowledge_id)
        record_audit_log(db, action="mcp_get_knowledge", resource=f"knowledge:{knowledge_id}", user_id=user.id if user else None, username=user.username if user else "mcp")
        return {
            "id": k.id,
            "space_id": k.space_id,
            "title": k.title,
            "content": k.content,
            "summary": k.summary,
            "content_type": k.content_type,
            "version": k.current_version_id,
            "tags": KnowledgeService._get_tags(db, k.id),
            "updated_at": str(k.updated_at)
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@mcp.tool(
    name="get_latest_knowledge",
    description="根据知识 ID 查询其最新生效版本的完整正文与快照说明。"
)
def get_latest_knowledge(knowledge_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        user = get_mcp_context_user(db)
        k = KnowledgeService.get_knowledge(db, knowledge_id)
        v = KnowledgeService.get_version(db, knowledge_id, k.current_version_id or 1)
        record_audit_log(db, action="mcp_get_latest_knowledge", resource=f"knowledge:{knowledge_id}", user_id=user.id if user else None, username=user.username if user else "mcp")
        return {
            "knowledge_id": k.id,
            "title": v.title,
            "content": v.content,
            "version_number": v.version_number,
            "change_summary": v.change_summary,
            "created_at": str(v.created_at)
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@mcp.tool(
    name="list_spaces",
    description="列出当前企业知识中心内当前身份有权访问的所有知识空间。"
)
def list_spaces() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        user = get_mcp_context_user(db)
        if not user:
            return []
        spaces = SpaceService.list_spaces_for_user(db, user)
        record_audit_log(db, action="mcp_list_spaces", resource="mcp_server", user_id=user.id, username=user.username)
        return [{"id": s.id, "name": s.name, "description": s.description, "visibility": s.visibility} for s in spaces]
    finally:
        db.close()

@mcp.tool(
    name="get_related_knowledge",
    description="根据指定的知识 ID，获取同一知识空间内的相关联文档建议列表。"
)
def get_related_knowledge(knowledge_id: int) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        k = KnowledgeService.get_knowledge(db, knowledge_id)
        from app.models.entities import Knowledge
        related = db.query(Knowledge).filter(
            Knowledge.space_id == k.space_id,
            Knowledge.id != k.id,
            Knowledge.is_deleted == False
        ).limit(5).all()
        return [{"id": r.id, "title": r.title, "summary": r.summary} for r in related]
    finally:
        db.close()

# ==================== MCP Resources 资源 URI 接口 ====================

@mcp.resource("knowledge://{knowledge_id}")
def read_knowledge_resource(knowledge_id: int) -> str:
    """直接通过标准 Resource URI 协议读取知识正文"""
    db = SessionLocal()
    try:
        k = KnowledgeService.get_knowledge(db, knowledge_id)
        return f"# {k.title}\n\n{k.content}"
    finally:
        db.close()

@mcp.resource("knowledge://space/{space_id}")
def read_space_resource(space_id: int) -> str:
    """直接通过标准 Resource URI 协议读取指定空间名下的知识目录概览"""
    db = SessionLocal()
    try:
        from app.models.entities import Knowledge
        docs = db.query(Knowledge).filter(Knowledge.space_id == space_id, Knowledge.is_deleted == False).all()
        lines = [f"- [#{d.id}] {d.title} (v{d.current_version_id or 1})" for d in docs]
        return "\n".join(lines) if lines else "该空间下暂无文档"
    finally:
        db.close()

if __name__ == "__main__":
    # 本地 STDIO 模式运行
    mcp.run()
