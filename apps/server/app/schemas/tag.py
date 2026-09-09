from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)

class TagResponse(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime]
    class Config:
        from_attributes = True
