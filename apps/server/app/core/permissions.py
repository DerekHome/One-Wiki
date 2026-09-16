from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.entities import User, Space, SpaceMember, Knowledge

ROLE_LEVELS = {
    "owner": 40,
    "admin": 30,
    "editor": 20,
    "viewer": 10
}

def check_admin(user: User):
    if getattr(user, "actor_type", None) == "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "AGENT_READ_ONLY", "message": "Agent 凭证不能执行管理操作"}
        )
    if user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "PERMISSION_DENIED", "message": "需要管理员权限"}
        )

def agent_space_allowed(user: User, space_id: int) -> bool:
    limit = getattr(user, "agent_space_id", None)
    if limit is None:
        return True
    return space_id == limit

def get_space_role(db: Session, space_id: int, user: User) -> str:
    if not agent_space_allowed(user, space_id):
        return "none"
    if user.role in ["owner", "admin"]:
        return "admin"
    space = db.query(Space).filter(Space.id == space_id, Space.is_deleted == False).first()
    if not space:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "知识空间不存在"})
    if space.owner_id == user.id:
        return "owner"
    member = db.query(SpaceMember).filter(SpaceMember.space_id == space_id, SpaceMember.user_id == user.id).first()
    if member:
        return member.role
    if space.visibility in ["public", "internal"]:
        return "viewer"
    return "none"

def check_space_permission(db: Session, space_id: int, user: User, required_role: str):
    user_role = get_space_role(db, space_id, user)
    if user_role == "none" or ROLE_LEVELS.get(user_role, 0) < ROLE_LEVELS.get(required_role, 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "PERMISSION_DENIED", "message": f"在当前空间需要至少 {required_role} 权限"}
        )

def can_access_knowledge(db: Session, knowledge: Knowledge, user: User, action: str = "read") -> bool:
    if not agent_space_allowed(user, knowledge.space_id):
        return False
    if user.role in ["owner", "admin"]:
        return True
    user_role = get_space_role(db, knowledge.space_id, user)
    if action == "read":
        return user_role != "none"
    elif action in ["write", "edit", "update"]:
        return ROLE_LEVELS.get(user_role, 0) >= ROLE_LEVELS.get("editor", 0)
    elif action in ["delete", "admin"]:
        return ROLE_LEVELS.get(user_role, 0) >= ROLE_LEVELS.get("admin", 0)
    return False
