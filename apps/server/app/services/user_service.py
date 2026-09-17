from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.entities import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from typing import List, Optional

class UserService:
    ALLOWED_ROLES = {"owner", "admin", "editor", "viewer"}
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> User:
        if UserService.get_by_username(db, data.username):
            raise HTTPException(status_code=400, detail={"code": "USER_EXISTS", "message": "用户名已存在"})
        role = data.role or "viewer"
        if role not in UserService.ALLOWED_ROLES:
            raise HTTPException(status_code=422, detail={"code": "INVALID_ROLE", "message": "无效的系统角色"})
        user = User(
            username=data.username,
            hashed_password=get_password_hash(data.password),
            role=role,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "用户不存在"})
        if data.role is not None:
            if data.role not in UserService.ALLOWED_ROLES:
                raise HTTPException(status_code=422, detail={"code": "INVALID_ROLE", "message": "无效的系统角色"})
            user.role = data.role
        if data.is_active is not None:
            user.is_active = data.is_active
        if data.password:
            user.hashed_password = get_password_hash(data.password)
            user.security_stamp = int(user.security_stamp or 0) + 1
        db.commit()
        db.refresh(user)
        return user
