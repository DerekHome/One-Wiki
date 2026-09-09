from sqlalchemy.orm import Session
from app.models.entities import AuditLog
from typing import Optional, Dict, Any

def record_audit_log(
    db: Session,
    action: str,
    resource: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
):
    log = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        resource=resource,
        details=details or {},
        ip_address=ip_address
    )
    db.add(log)
    try:
        db.commit()
    except Exception:
        db.rollback()
