from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.models.entities import Knowledge, Space, SpaceMember, Tag, KnowledgeTag, User
from typing import List, Optional

class SearchService:
    @staticmethod
    def search(
        db: Session,
        query_str: str,
        user: User,
        space_id: Optional[int] = None,
        knowledge_type: Optional[str] = None,
        tag_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ):
        from app.core.modules.registry import module_registry
        if not module_registry.is_enabled("search"):
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

        if user.role in ["owner", "admin"]:
            allowed_spaces = db.query(Space.id).filter(Space.is_deleted == False).all()
        else:
            member_spaces = [m.space_id for m in db.query(SpaceMember.space_id).filter(SpaceMember.user_id == user.id).all()]
            allowed_spaces = db.query(Space.id).filter(
                Space.is_deleted == False,
                (Space.visibility.in_(["public", "internal"])) | (Space.id.in_(member_spaces))
            ).all()

        allowed_space_ids = [s[0] for s in allowed_spaces]
        if not allowed_space_ids:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

        filters = [
            Knowledge.is_deleted == False,
            Knowledge.status == "published",
            Knowledge.space_id.in_(allowed_space_ids)
        ]

        if space_id:
            if space_id not in allowed_space_ids:
                return {"items": [], "total": 0, "page": page, "page_size": page_size}
            filters.append(Knowledge.space_id == space_id)

        if knowledge_type:
            filters.append(Knowledge.knowledge_type == knowledge_type)

        if tag_name:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                return {"items": [], "total": 0, "page": page, "page_size": page_size}
            k_ids_with_tag = [kt.knowledge_id for kt in db.query(KnowledgeTag.knowledge_id).filter(KnowledgeTag.tag_id == tag.id).all()]
            filters.append(Knowledge.id.in_(k_ids_with_tag))

        if query_str:
            q_clean = query_str.strip()
            filters.append(or_(
                Knowledge.title.ilike(f"%{q_clean}%"),
                Knowledge.content.ilike(f"%{q_clean}%"),
                Knowledge.summary.ilike(f"%{q_clean}%")
            ))

        total = db.query(func.count(Knowledge.id)).filter(and_(*filters)).scalar() or 0
        results = db.query(Knowledge).filter(and_(*filters)).order_by(Knowledge.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for k in results:
            content_lower = k.content.lower()
            q_pos = content_lower.find(query_str.lower()) if query_str else -1
            if q_pos != -1:
                start = max(0, q_pos - 40)
                end = min(len(k.content), q_pos + len(query_str) + 60)
                snippet = "..." + k.content[start:end] + "..."
            else:
                snippet = k.summary or (k.content[:100] + "...")

            items.append({
                "knowledge_id": k.id,
                "title": k.title,
                "snippet": snippet,
                "score": 1.0,
                "source": k.source_type,
                "version": k.current_version_id,
                "space_id": k.space_id,
                "updated_at": k.updated_at
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
