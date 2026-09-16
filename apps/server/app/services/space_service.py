from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.entities import Space, SpaceMember, User
from app.schemas.space import SpaceCreate, SpaceUpdate, SpaceMemberAdd
from app.core.permissions import resolve_agent_space_ids
from typing import List, Optional

class SpaceService:
    @staticmethod
    def create_space(db: Session, data: SpaceCreate, owner_id: int) -> Space:
        existing = db.query(Space).filter(Space.name == data.name, Space.is_deleted == False).first()
        if existing:
            raise HTTPException(status_code=400, detail={"code": "SPACE_EXISTS", "message": "同名空间已存在"})
        space = Space(
            name=data.name,
            description=data.description,
            owner_id=owner_id,
            visibility=data.visibility or "internal",
            is_deleted=False
        )
        db.add(space)
        db.commit()
        db.refresh(space)
        member = SpaceMember(space_id=space.id, user_id=owner_id, role="owner")
        db.add(member)
        db.commit()
        return space

    @staticmethod
    def list_spaces_for_user(db: Session, user: User) -> List[Space]:
        if user.role in ["owner", "admin"]:
            spaces = db.query(Space).filter(Space.is_deleted == False).all()
        else:
            my_space_ids = [m.space_id for m in db.query(SpaceMember.space_id).filter(SpaceMember.user_id == user.id).all()]
            spaces = db.query(Space).filter(
                Space.is_deleted == False,
                (Space.visibility.in_(["public", "internal"])) | (Space.id.in_(my_space_ids))
            ).all()
        limit = resolve_agent_space_ids(user)
        if limit is None:
            return spaces
        allowed = set(limit)
        return [space for space in spaces if space.id in allowed]

    @staticmethod
    def get_space(db: Session, space_id: int) -> Space:
        space = db.query(Space).filter(Space.id == space_id, Space.is_deleted == False).first()
        if not space:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "空间不存在"})
        return space

    @staticmethod
    def update_space(db: Session, space_id: int, data: SpaceUpdate) -> Space:
        space = SpaceService.get_space(db, space_id)
        if data.name is not None:
            space.name = data.name
        if data.description is not None:
            space.description = data.description
        if data.visibility is not None:
            space.visibility = data.visibility
        db.commit()
        db.refresh(space)
        return space

    @staticmethod
    def delete_space(db: Session, space_id: int):
        space = SpaceService.get_space(db, space_id)
        space.is_deleted = True
        db.commit()

    @staticmethod
    def list_members(db: Session, space_id: int):
        members = db.query(SpaceMember).filter(SpaceMember.space_id == space_id).all()
        result = []
        for m in members:
            user = db.query(User).filter(User.id == m.user_id).first()
            result.append({
                "id": m.id,
                "space_id": m.space_id,
                "user_id": m.user_id,
                "role": m.role,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role
                } if user else None
            })
        return result

    @staticmethod
    def add_or_update_member(db: Session, space_id: int, data: SpaceMemberAdd) -> SpaceMember:
        if not db.query(Space).filter(Space.id == space_id, Space.is_deleted == False).first():
            raise HTTPException(status_code=404, detail={"code": "SPACE_NOT_FOUND", "message": "知识空间不存在"})
        if not db.query(User).filter(User.id == data.user_id, User.is_active == True).first():
            raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND", "message": "用户不存在或已禁用"})
        member = db.query(SpaceMember).filter(SpaceMember.space_id == space_id, SpaceMember.user_id == data.user_id).first()
        if member:
            member.role = data.role
        else:
            member = SpaceMember(space_id=space_id, user_id=data.user_id, role=data.role)
            db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def remove_member(db: Session, space_id: int, user_id: int):
        space = SpaceService.get_space(db, space_id)
        if space.owner_id == user_id:
            raise HTTPException(status_code=400, detail={"code": "OWNER_CANNOT_REMOVE", "message": "空间所有者不能被移除"})
        member = db.query(SpaceMember).filter(SpaceMember.space_id == space_id, SpaceMember.user_id == user_id).first()
        if member:
            db.delete(member)
            db.commit()
