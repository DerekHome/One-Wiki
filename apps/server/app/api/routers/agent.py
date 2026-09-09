from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User, Space, Knowledge, KnowledgeVersion
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.permissions import check_space_permission, can_access_knowledge
from app.services.knowledge_service import KnowledgeService
from app.services.space_service import SpaceService
from app.services.search_service import SearchService
from app.core.audit import record_audit_log
from typing import List, Optional, Dict, Any

router = APIRouter()

@router.get("/spaces")
def agent_list_spaces(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    spaces = SpaceService.list_spaces_for_user(db, current_user)
    record_audit_log(db, action="agent_list_spaces", resource="agent_api", user_id=current_user.id, username=current_user.username)
    return ResponseModel(data=[{"id": s.id, "name": s.name, "description": s.description, "visibility": s.visibility} for s in spaces])

@router.get("/knowledge/{id}")
def agent_get_knowledge(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, id)
    if not can_access_knowledge(db, k, current_user, "read"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "Agent 权限不足，无法访问该知识"})
    record_audit_log(db, action="agent_get_knowledge", resource=f"knowledge:{id}", user_id=current_user.id, username=current_user.username)
    return ResponseModel(data={
        "knowledge_id": k.id,
        "title": k.title,
        "content": k.content,
        "summary": k.summary,
        "version": k.current_version_id,
        "source": k.source_type,
        "updated_at": k.updated_at
    })

@router.get("/knowledge/{id}/latest")
def agent_get_latest_knowledge(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, id)
    if not can_access_knowledge(db, k, current_user, "read"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "Agent 权限不足，无法访问该知识"})
    record_audit_log(db, action="agent_get_latest", resource=f"knowledge:{id}", user_id=current_user.id, username=current_user.username)
    return ResponseModel(data={
        "knowledge_id": k.id,
        "title": k.title,
        "content": k.content,
        "version": k.current_version_id,
        "source": k.source_type,
        "updated_at": k.updated_at
    })

@router.get("/knowledge/{id}/versions")
def agent_get_versions(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, id)
    if not can_access_knowledge(db, k, current_user, "read"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "Agent 权限不足，无法访问该知识历史版本"})
    versions = KnowledgeService.list_versions(db, id)
    record_audit_log(db, action="agent_get_versions", resource=f"knowledge:{id}", user_id=current_user.id, username=current_user.username)
    return ResponseModel(data=[
        {
            "version_number": v.version_number,
            "title": v.title,
            "change_summary": v.change_summary,
            "created_at": v.created_at
        } for v in versions
    ])

@router.get("/related/{id}")
def agent_get_related(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, id)
    if not can_access_knowledge(db, k, current_user, "read"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "Agent 权限不足"})
    # 返回同空间内关联知识
    related = db.query(Knowledge).filter(Knowledge.space_id == k.space_id, Knowledge.id != k.id, Knowledge.is_deleted == False).limit(5).all()
    return ResponseModel(data=[{"knowledge_id": r.id, "title": r.title} for r in related])

@router.get("/search")
def agent_search_get(
    q: str = Query("", description="查询词"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = SearchService.search(db, q, current_user, page=1, page_size=limit)
    record_audit_log(db, action="agent_search", resource="agent_api", user_id=current_user.id, username=current_user.username, details={"query": q})
    return ResponseModel(data=results.get("items", []))

@router.post("/search")
def agent_search_post(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = payload.get("query", "")
    space_ids = payload.get("space_ids", [])
    types = payload.get("types", [])
    limit = payload.get("limit", 10)

    # 限制单空间或所有空间
    target_space_id = space_ids[0] if space_ids else None
    target_type = types[0] if types else None

    results = SearchService.search(
        db=db,
        query_str=query,
        user=current_user,
        space_id=target_space_id,
        knowledge_type=target_type,
        page=1,
        page_size=limit
    )
    record_audit_log(db, action="agent_search", resource="agent_api", user_id=current_user.id, username=current_user.username, details=payload)
    return ResponseModel(data=results.get("items", []))
