from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AttachmentResponse(BaseModel):
    id: int
    knowledge_id: Optional[int]
    filename: str
    mime_type: Optional[str]
    size: int
    checksum: Optional[str]
    created_at: Optional[datetime]
    class Config:
        from_attributes = True
