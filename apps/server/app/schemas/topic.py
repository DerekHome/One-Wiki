from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TopicBase(BaseModel):
    name: str = Field(..., max_length=128, description="专题名称")
    description: Optional[str] = Field(None, description="专题描述与简介")
    sort_order: Optional[int] = Field(0, description="排序权重")

class TopicCreate(TopicBase):
    space_id: int = Field(..., description="所属知识空间ID")

class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None
    sort_order: Optional[int] = None

class TopicResponse(TopicBase):
    id: int
    space_id: int
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
