from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: Optional[str] = "viewer"


class PublicUserCreate(UserBase):
    """公开注册输入，不允许客户端提交系统角色。"""
    model_config = ConfigDict(extra="forbid")
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
