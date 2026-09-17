from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.permissions import check_admin
from app.services.user_service import UserService
from app.core.audit import record_audit_log
from typing import List

router = APIRouter()

@router.get("/", response_model=ResponseModel[List[UserResponse]])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin(current_user)
    users = UserService.list_users(db, skip=skip, limit=limit)
    return ResponseModel(data=[UserResponse.model_validate(u) for u in users])

@router.post("/", response_model=ResponseModel[UserResponse])
def create_user(
    data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin(current_user)
    user = UserService.create_user(db, data)
    record_audit_log(db, action="create_user", resource=f"user:{user.id}", user_id=current_user.id, username=current_user.username, details={"created_username": user.username})
    return ResponseModel(data=UserResponse.model_validate(user))

@router.put("/{user_id}", response_model=ResponseModel[UserResponse])
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin(current_user)
    user = UserService.update_user(db, user_id, data)
    record_audit_log(db, action="update_user", resource=f"user:{user.id}", user_id=current_user.id, username=current_user.username, details=data.model_dump(exclude_unset=True))
    return ResponseModel(data=UserResponse.model_validate(user))
