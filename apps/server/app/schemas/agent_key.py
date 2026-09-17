from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=512)
    space_id: Optional[int] = None
    space_ids: Optional[List[int]] = None
    permissions: Optional[List[str]] = None


class AgentApiKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=512)
    space_ids: Optional[List[int]] = None
    permissions: Optional[List[str]] = None


class AgentApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None
    key_prefix: str
    space_id: Optional[int] = None
    space_ids: List[int] = []
    permissions: List[str] = []
    owner_user_id: int
    owner_username: Optional[str] = None
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class AgentApiKeyCreatedResponse(AgentApiKeyResponse):
    api_key: str
