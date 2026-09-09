from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User, Space
from app.schemas.space import SpaceCreate, SpaceUpdate, SpaceResponse, SpaceMemberAdd, SpaceMemberResponse
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.permissions import check_space_permission
from app.services.space_service import SpaceService
from app.core.audit import record_audit_log
from typing import List

router = APIRouter()

@router.get("/", response_model=ResponseModel[List[SpaceResponse]])
def list_spaces(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    spaces = SpaceService.list_spaces_for_user(db, current_user)
    return ResponseModel(data=[SpaceResponse.model_validate(s) for s in spaces])

@router.post("/", response_model=ResponseModel[SpaceResponse])
def create_space(data: SpaceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    space = SpaceService.create_space(db, data, owner_id=current_user.id)
    record_audit_log(db, action="create_space", resource=f"space:{space.id}", user_id=current_user.id, username=current_user.username, details={"name": space.name})
    return ResponseModel(data=SpaceResponse.model_validate(space))

@router.get("/{space_id}", response_model=ResponseModel[SpaceResponse])
def get_space(space_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, space_id, current_user, "viewer")
    space = SpaceService.get_space(db, space_id)
    return ResponseModel(data=SpaceResponse.model_validate(space))

@router.put("/{space_id}", response_model=ResponseModel[SpaceResponse])
def update_space(space_id: int, data: SpaceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, space_id, current_user, "admin")
    space = SpaceService.update_space(db, space_id, data)
    record_audit_log(db, action="update_space", resource=f"space:{space.id}", user_id=current_user.id, username=current_user.username, details=data.model_dump(exclude_unset=True))
    return ResponseModel(data=SpaceResponse.model_validate(space))

@router.delete("/{space_id}", response_model=ResponseModel[dict])
def delete_space(space_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, space_id, current_user, "owner")
    SpaceService.delete_space(db, space_id)
    record_audit_log(db, action="delete_space", resource=f"space:{space_id}", user_id=current_user.id, username=current_user.username)
    return ResponseModel(data={"message": "空间已删除"})

@router.get("/{space_id}/members", response_model=ResponseModel[List[dict]])
def list_members(space_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, space_id, current_user, "viewer")
    members = SpaceService.list_members(db, space_id)
    return ResponseModel(data=members)

@router.post("/{space_id}/members", response_model=ResponseModel[dict])
def add_member(space_id: int, data: SpaceMemberAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, space_id, current_user, "admin")
    member = SpaceService.add_or_update_member(db, space_id, data)
    record_audit_log(db, action="add_space_member", resource=f"space:{space_id}", user_id=current_user.id, username=current_user.username, details={"member_user_id": data.user_id, "role": data.role})
    return ResponseModel(data={"id": member.id, "space_id": member.space_id, "user_id": member.user_id, "role": member.role})

@router.delete("/{space_id}/members/{user_id}", response_model=ResponseModel[dict])
def remove_member(space_id: int, user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, space_id, current_user, "admin")
    SpaceService.remove_member(db, space_id, user_id)
    record_audit_log(db, action="remove_space_member", resource=f"space:{space_id}", user_id=current_user.id, username=current_user.username, details={"removed_user_id": user_id})
    return ResponseModel(data={"message": "成员已移除"})

@router.get("/{space_id}/topics", response_model=ResponseModel[List[dict]])
def list_space_topics(space_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, space_id, current_user, "viewer")
    from app.services.topic_service import TopicService
    topics = TopicService.list_topics_by_space(db, space_id)
    return ResponseModel(data=[
        {
            "id": t.id,
            "space_id": t.space_id,
            "name": t.name,
            "description": t.description,
            "sort_order": t.sort_order,
            "created_at": t.created_at
        } for t in topics
    ])

@router.post("/{space_id}/topics", response_model=ResponseModel[dict])
def create_space_topic(space_id: int, data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, space_id, current_user, "editor")
    from app.services.topic_service import TopicService
    from app.schemas.topic import TopicCreate
    topic_data = TopicCreate(
        space_id=space_id,
        name=data.get("name"),
        description=data.get("description"),
        sort_order=data.get("sort_order", 0)
    )
    topic = TopicService.create_topic(db, topic_data)
    record_audit_log(db, action="create_topic", resource=f"topic:{topic.id}", user_id=current_user.id, username=current_user.username, details={"name": topic.name, "space_id": space_id})
    return ResponseModel(data={"id": topic.id, "space_id": topic.space_id, "name": topic.name})

@router.delete("/{space_id}/topics/{topic_id}", response_model=ResponseModel[dict])
def delete_space_topic(space_id: int, topic_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, space_id, current_user, "admin")
    from app.services.topic_service import TopicService
    topic = TopicService.get_topic(db, topic_id)
    if topic.space_id != space_id:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "专题不存在"})
    TopicService.delete_topic(db, topic_id)
    record_audit_log(db, action="delete_topic", resource=f"topic:{topic_id}", user_id=current_user.id, username=current_user.username)
    return ResponseModel(data={"message": "专题已删除"})
