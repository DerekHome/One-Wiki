from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User, AuditLog
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.permissions import check_admin
from typing import List, Optional

router = APIRouter()

@router.get("/")
def list_audit_logs(
    action: Optional[str] = None,
    username: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin(current_user)
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if username:
        query = query.filter(AuditLog.username == username)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ResponseModel(data={
        "items": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "username": a.username,
                "action": a.action,
                "resource": a.resource,
                "details": a.details,
                "created_at": a.created_at
            } for a in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    })
