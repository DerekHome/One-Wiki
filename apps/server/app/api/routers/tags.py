from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.permissions import check_admin
from app.services.tag_service import TagService
from app.core.audit import record_audit_log
from typing import List

router = APIRouter()

@router.get("/", response_model=ResponseModel[List[TagResponse]])
def list_tags(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tags = TagService.list_tags(db)
    return ResponseModel(data=[TagResponse.model_validate(t) for t in tags])

@router.post("/", response_model=ResponseModel[TagResponse])
def create_tag(data: TagCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tag = TagService.create_tag(db, data)
    record_audit_log(db, action="create_tag", resource=f"tag:{tag.id}", user_id=current_user.id, username=current_user.username, details={"name": tag.name})
    return ResponseModel(data=TagResponse.model_validate(tag))

@router.delete("/{tag_id}", response_model=ResponseModel[dict])
def delete_tag(tag_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    TagService.delete_tag(db, tag_id)
    record_audit_log(db, action="delete_tag", resource=f"tag:{tag_id}", user_id=current_user.id, username=current_user.username)
    return ResponseModel(data={"message": "标签已删除"})
