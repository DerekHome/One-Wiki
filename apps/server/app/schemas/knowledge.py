from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class KnowledgeCreate(BaseModel):
    space_id: int
    topic_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    summary: Optional[str] = None
    knowledge_type: Optional[str] = "article"
    tags: Optional[List[str]] = []

class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    topic_id: Optional[int] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    knowledge_type: Optional[str] = None
    tags: Optional[List[str]] = None
    change_summary: Optional[str] = None

class KnowledgeVersionResponse(BaseModel):
    id: int
    knowledge_id: int
    version_number: int
    title: str
    content: str
    change_summary: Optional[str]
    created_by: Optional[int]
    created_at: Optional[datetime]
    class Config:
        from_attributes = True

class KnowledgeResponse(BaseModel):
    id: int
    space_id: int
    topic_id: Optional[int] = None
    title: str
    summary: Optional[str]
    content: str
    content_type: str
    knowledge_type: str
    source_type: Optional[str] = "manual"
    source_uri: Optional[str] = None
    status: str
    visibility: str
    owner_id: Optional[int]
    current_version_id: Optional[int]
    tags: Optional[List[str]] = []
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    class Config:
        from_attributes = True

class VersionDiffResponse(BaseModel):
    version_from: int
    version_to: int
    title_diff: Dict[str, Any]
    content_diff: List[str]
