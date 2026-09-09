from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse

class SpaceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    description: Optional[str] = None
    visibility: Optional[str] = "internal"

class SpaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None

class SpaceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: Optional[int]
    visibility: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True

class SpaceMemberAdd(BaseModel):
    user_id: int
    role: str = Field("viewer", pattern="^(admin|editor|viewer)$")  # admin, editor, viewer

class SpaceMemberResponse(BaseModel):
    id: int
    space_id: int
    user_id: int
    role: str
    user: Optional[UserResponse] = None
    class Config:
        from_attributes = True
