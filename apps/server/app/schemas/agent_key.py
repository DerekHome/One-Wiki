from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    space_id: Optional[int] = None


class AgentApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    space_id: Optional[int] = None
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentApiKeyCreatedResponse(AgentApiKeyResponse):
    api_key: str
