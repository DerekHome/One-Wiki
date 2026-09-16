from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import can_access_knowledge, check_space_permission, require_agent_permission
from app.models.entities import Knowledge, KnowledgeTag, KnowledgeVersion, User
from app.services.agent_key_service import KEY_PREFIX, AgentKeyService
from app.services.attachment_service import AttachmentService
from app.services.knowledge_service import KnowledgeService
from app.services.search_service import SearchService
from app.services.space_service import SpaceService
from app.services.topic_service import TopicService


class AgentKnowledgeService:
    """人与 Agent 共用的只读知识契约：已发布、可引用、走同一套权限。"""

    @staticmethod
    def citation_uri(knowledge_id: int) -> str:
        return f"knowledge://{knowledge_id}"

    @staticmethod
    def is_agent_visible(knowledge: Knowledge) -> bool:
        if knowledge.is_deleted or knowledge.status != "published":
            return False
        if knowledge.expired_at is None:
            return True
        expired_at = knowledge.expired_at
        if expired_at.tzinfo is None:
            expired_at = expired_at.replace(tzinfo=timezone.utc)
        return expired_at > datetime.now(timezone.utc)

    @staticmethod
    def resolve_mcp_user(db: Session, username: Optional[str]) -> User:
        identity = (username or "").strip()
        if not identity:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "MCP_AUTH_REQUIRED", "message": "未配置 MCP_AUTH_USER，拒绝回落到管理员身份"},
            )
        user = db.query(User).filter(User.username == identity, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "MCP_AUTH_INVALID", "message": "MCP 执行身份不存在或已停用"},
            )
        user.actor_type = "human"
        return user

    @staticmethod
    def resolve_mcp_principal(db: Session, username: Optional[str] = None, api_key: Optional[str] = None) -> User:
        raw_key = (api_key or "").strip()
        if raw_key:
            if not raw_key.startswith(KEY_PREFIX):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "MCP_AUTH_INVALID", "message": "MCP_API_KEY 格式无效"},
                )
            return AgentKeyService.authenticate(db, raw_key)
        return AgentKnowledgeService.resolve_mcp_user(db, username)

    @staticmethod
    def get_current_version(db: Session, knowledge: Knowledge) -> Optional[KnowledgeVersion]:
        if knowledge.current_version_id:
            version = db.query(KnowledgeVersion).filter(
                KnowledgeVersion.id == knowledge.current_version_id,
                KnowledgeVersion.knowledge_id == knowledge.id,
            ).first()
            if version:
                return version
        return (
            db.query(KnowledgeVersion)
            .filter(KnowledgeVersion.knowledge_id == knowledge.id)
            .order_by(KnowledgeVersion.version_number.desc())
            .first()
        )

    @staticmethod
    def require_readable(db: Session, knowledge_id: int, user: User) -> Knowledge:
        knowledge = KnowledgeService.get_knowledge(db, knowledge_id)
        if not can_access_knowledge(db, knowledge, user, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "PERMISSION_DENIED", "message": "Agent 权限不足，无法访问该知识"},
            )
        if not AgentKnowledgeService.is_agent_visible(knowledge):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "KNOWLEDGE_NOT_AVAILABLE", "message": "知识未发布或不对 Agent 开放"},
            )
        return knowledge

    @staticmethod
    def serialize(
        db: Session,
        knowledge: Knowledge,
        *,
        include_content: bool = True,
        version: Optional[KnowledgeVersion] = None,
        snippet: Optional[str] = None,
    ) -> Dict[str, Any]:
        version = version or AgentKnowledgeService.get_current_version(db, knowledge)
        version_number = version.version_number if version else 1
        title = version.title if version else knowledge.title
        content = version.content if version else knowledge.content
        topic_name = None
        if knowledge.topic_id:
            try:
                topic_name = TopicService.get_topic(db, knowledge.topic_id).name
            except HTTPException:
                topic_name = None

        payload: Dict[str, Any] = {
            "knowledge_id": knowledge.id,
            "title": title,
            "summary": knowledge.summary,
            "version": version_number,
            "version_number": version_number,
            "source": knowledge.source_type,
            "source_uri": knowledge.source_uri,
            "citation_uri": AgentKnowledgeService.citation_uri(knowledge.id),
            "space_id": knowledge.space_id,
            "topic_id": knowledge.topic_id,
            "topic": topic_name,
            "tags": KnowledgeService._get_tags(db, knowledge.id),
            "status": knowledge.status,
            "published_at": knowledge.published_at,
            "updated_at": knowledge.updated_at,
        }
        if include_content:
            payload["content"] = content
        if snippet is not None:
            payload["snippet"] = snippet
        return payload

    @staticmethod
    def get_knowledge(db: Session, knowledge_id: int, user: User) -> Dict[str, Any]:
        require_agent_permission(user, "read")
        knowledge = AgentKnowledgeService.require_readable(db, knowledge_id, user)
        return AgentKnowledgeService.serialize(db, knowledge, include_content=True)

    @staticmethod
    def get_latest_knowledge(db: Session, knowledge_id: int, user: User) -> Dict[str, Any]:
        require_agent_permission(user, "read")
        knowledge = AgentKnowledgeService.require_readable(db, knowledge_id, user)
        version = AgentKnowledgeService.get_current_version(db, knowledge)
        return AgentKnowledgeService.serialize(db, knowledge, include_content=True, version=version)

    @staticmethod
    def list_versions(db: Session, knowledge_id: int, user: User) -> List[Dict[str, Any]]:
        require_agent_permission(user, "versions")
        knowledge = AgentKnowledgeService.require_readable(db, knowledge_id, user)
        versions = KnowledgeService.list_versions(db, knowledge.id)
        return [
            {
                "version_number": item.version_number,
                "title": item.title,
                "change_summary": item.change_summary,
                "created_at": item.created_at,
                "citation_uri": AgentKnowledgeService.citation_uri(knowledge.id),
            }
            for item in versions
        ]

    @staticmethod
    def list_spaces(db: Session, user: User) -> List[Dict[str, Any]]:
        require_agent_permission(user, "list_spaces")
        spaces = SpaceService.list_spaces_for_user(db, user)
        return [
            {"id": space.id, "name": space.name, "description": space.description, "visibility": space.visibility}
            for space in spaces
        ]

    @staticmethod
    def list_related(db: Session, knowledge_id: int, user: User, limit: int = 5) -> List[Dict[str, Any]]:
        require_agent_permission(user, "related")
        knowledge = AgentKnowledgeService.require_readable(db, knowledge_id, user)
        candidates = (
            db.query(Knowledge)
            .filter(
                Knowledge.space_id == knowledge.space_id,
                Knowledge.id != knowledge.id,
                Knowledge.is_deleted == False,
                Knowledge.status == "published",
            )
            .order_by(Knowledge.updated_at.desc())
            .all()
        )

        tag_ids = {
            row.tag_id
            for row in db.query(KnowledgeTag.tag_id).filter(KnowledgeTag.knowledge_id == knowledge.id).all()
        }

        def rank(item: Knowledge) -> tuple:
            same_topic = 0 if knowledge.topic_id and item.topic_id == knowledge.topic_id else 1
            item_tags = {
                row.tag_id
                for row in db.query(KnowledgeTag.tag_id).filter(KnowledgeTag.knowledge_id == item.id).all()
            }
            same_tag = 0 if tag_ids and item_tags.intersection(tag_ids) else 1
            return (same_topic, same_tag)

        ranked = sorted(candidates, key=rank)
        results: List[Dict[str, Any]] = []
        for item in ranked:
            if not can_access_knowledge(db, item, user, "read"):
                continue
            if not AgentKnowledgeService.is_agent_visible(item):
                continue
            results.append(
                {
                    "knowledge_id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "citation_uri": AgentKnowledgeService.citation_uri(item.id),
                    "topic_id": item.topic_id,
                }
            )
            if len(results) >= limit:
                break
        return results

    @staticmethod
    def list_published_in_space(db: Session, space_id: int, user: User) -> List[Knowledge]:
        require_agent_permission(user, "read")
        check_space_permission(db, space_id, user, "viewer")
        docs = (
            db.query(Knowledge)
            .filter(Knowledge.space_id == space_id, Knowledge.is_deleted == False, Knowledge.status == "published")
            .order_by(Knowledge.updated_at.desc())
            .all()
        )
        return [doc for doc in docs if AgentKnowledgeService.is_agent_visible(doc)]

    @staticmethod
    def list_topics(db: Session, space_id: int, user: User) -> List[Dict[str, Any]]:
        require_agent_permission(user, "list_spaces")
        check_space_permission(db, space_id, user, "viewer")
        topics = TopicService.list_topics_by_space(db, space_id)
        return [
            {
                "id": topic.id,
                "space_id": topic.space_id,
                "name": topic.name,
                "description": topic.description,
                "sort_order": topic.sort_order,
            }
            for topic in topics
        ]

    @staticmethod
    def list_attachments(db: Session, knowledge_id: int, user: User) -> List[Dict[str, Any]]:
        require_agent_permission(user, "attachments")
        knowledge = AgentKnowledgeService.require_readable(db, knowledge_id, user)
        attachments = AttachmentService.list_attachments(db, knowledge.id)
        return [
            {
                "id": item.id,
                "filename": item.filename,
                "mime_type": item.mime_type,
                "size": item.size,
                "knowledge_id": knowledge.id,
                "citation_uri": AgentKnowledgeService.citation_uri(knowledge.id),
            }
            for item in attachments
        ]

    @staticmethod
    def search(
        db: Session,
        user: User,
        query: str,
        *,
        space_id: Optional[int] = None,
        knowledge_type: Optional[str] = None,
        topic_id: Optional[int] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        from app.core.modules.registry import module_registry

        require_agent_permission(user, "search")
        if not module_registry.is_enabled("search"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "SEARCH_MODULE_DISABLED", "message": "检索模块未启用"},
            )

        results = SearchService.search(
            db=db,
            query_str=query,
            user=user,
            space_id=space_id,
            knowledge_type=knowledge_type,
            topic_id=topic_id,
            page=1,
            page_size=limit,
        )
        items = []
        for hit in results.get("items", []):
            knowledge = KnowledgeService.get_knowledge(db, hit["knowledge_id"])
            if not AgentKnowledgeService.is_agent_visible(knowledge):
                continue
            payload = AgentKnowledgeService.serialize(
                db,
                knowledge,
                include_content=False,
                snippet=hit.get("snippet"),
            )
            payload["score"] = hit.get("score", 1.0)
            items.append(payload)
        return items
