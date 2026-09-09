from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.services.search_service import SearchService
from app.core.audit import record_audit_log
from typing import Optional

router = APIRouter()

@router.get("/")
def search(
    q: str = Query("", description="搜索关键词"),
    space_id: Optional[int] = Query(None, description="限定知识空间"),
    knowledge_type: Optional[str] = Query(None, description="知识类型"),
    tag: Optional[str] = Query(None, description="标签"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = SearchService.search(
        db=db,
        query_str=q,
        user=current_user,
        space_id=space_id,
        knowledge_type=knowledge_type,
        tag_name=tag,
        page=page,
        page_size=page_size
    )
    record_audit_log(db, action="search", resource="search_engine", user_id=current_user.id, username=current_user.username, details={"query": q, "space_id": space_id, "tag": tag})
    return ResponseModel(data=results)
