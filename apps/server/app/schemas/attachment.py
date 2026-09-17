from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    knowledge_id: Optional[int]
    filename: str
    mime_type: Optional[str]
    size: int
    checksum: Optional[str]
    created_at: Optional[datetime]
