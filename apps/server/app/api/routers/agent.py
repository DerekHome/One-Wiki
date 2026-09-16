from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import User
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.audit import record_audit_log
from app.services.agent_knowledge_service import AgentKnowledgeService
from typing import Any, Dict, Optional

router = APIRouter()


def _audit_user(user: User):
    if getattr(user, "actor_type", None) == "agent":
        return f"agent:{getattr(user, 'agent_key_name', None) or user.username}"
    return user.username


def _audit_details(user: User, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    details = extra.copy() if extra else {}
    details["actor_type"] = getattr(user, "actor_type", "human")
    if getattr(user, "agent_key_id", None):
        details["agent_key_id"] = user.agent_key_id
        details["agent_key_name"] = user.agent_key_name
    return details


@router.get("/spaces")
def agent_list_spaces(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = AgentKnowledgeService.list_spaces(db, current_user)
    record_audit_log(db, action="agent_list_spaces", resource="agent_api", user_id=current_user.id, username=_audit_user(current_user), details=_audit_details(current_user))
    return ResponseModel(data=data)


@router.get("/knowledge/{id}")
def agent_get_knowledge(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = AgentKnowledgeService.get_knowledge(db, id, current_user)
    record_audit_log(db, action="agent_get_knowledge", resource=f"knowledge:{id}", user_id=current_user.id, username=_audit_user(current_user), details=_audit_details(current_user))
    return ResponseModel(data=data)


@router.get("/knowledge/{id}/latest")
def agent_get_latest_knowledge(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = AgentKnowledgeService.get_latest_knowledge(db, id, current_user)
    record_audit_log(db, action="agent_get_latest", resource=f"knowledge:{id}", user_id=current_user.id, username=_audit_user(current_user), details=_audit_details(current_user))
    return ResponseModel(data=data)


@router.get("/knowledge/{id}/versions")
def agent_get_versions(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = AgentKnowledgeService.list_versions(db, id, current_user)
    record_audit_log(db, action="agent_get_versions", resource=f"knowledge:{id}", user_id=current_user.id, username=_audit_user(current_user), details=_audit_details(current_user))
    return ResponseModel(data=data)


@router.get("/related/{id}")
def agent_get_related(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = AgentKnowledgeService.list_related(db, id, current_user)
    record_audit_log(db, action="agent_get_related", resource=f"knowledge:{id}", user_id=current_user.id, username=_audit_user(current_user), details=_audit_details(current_user))
    return ResponseModel(data=data)


@router.get("/search")
def agent_search_get(
    q: str = Query("", description="查询词"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = AgentKnowledgeService.search(db, current_user, q, limit=limit)
    record_audit_log(db, action="agent_search", resource="agent_api", user_id=current_user.id, username=_audit_user(current_user), details=_audit_details(current_user, {"query": q}))
    return ResponseModel(data=data)


@router.post("/search")
def agent_search_post(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = payload.get("query", "")
    space_ids = payload.get("space_ids", [])
    types = payload.get("types", [])
    topic_id = payload.get("topic_id")
    limit = payload.get("limit", 10)
    target_space_id = space_ids[0] if space_ids else None
    target_type = types[0] if types else None
    data = AgentKnowledgeService.search(
        db,
        current_user,
        query,
        space_id=target_space_id,
        knowledge_type=target_type,
        topic_id=topic_id,
        limit=limit,
    )
    record_audit_log(db, action="agent_search", resource="agent_api", user_id=current_user.id, username=_audit_user(current_user), details=_audit_details(current_user, payload))
    return ResponseModel(data=data)


@router.get("/spaces/{space_id}/topics")
def agent_list_topics(space_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = AgentKnowledgeService.list_topics(db, space_id, current_user)
    record_audit_log(db, action="agent_list_topics", resource=f"space:{space_id}", user_id=current_user.id, username=_audit_user(current_user), details=_audit_details(current_user))
    return ResponseModel(data=data)


@router.get("/knowledge/{id}/attachments")
def agent_list_attachments(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = AgentKnowledgeService.list_attachments(db, id, current_user)
    record_audit_log(db, action="agent_list_attachments", resource=f"knowledge:{id}", user_id=current_user.id, username=_audit_user(current_user), details=_audit_details(current_user))
    return ResponseModel(data=data)
