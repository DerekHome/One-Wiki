from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import User
from app.schemas.common import ResponseModel
from app.schemas.agent_key import AgentApiKeyCreate, AgentApiKeyCreatedResponse, AgentApiKeyResponse
from app.core.security import get_current_user
from app.core.audit import record_audit_log
from app.services.agent_key_service import AgentKeyService
from typing import List

router = APIRouter()


@router.get("/", response_model=ResponseModel[List[AgentApiKeyResponse]])
def list_agent_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = AgentKeyService.list_keys(db, current_user)
    return ResponseModel(data=[AgentApiKeyResponse.model_validate(key) for key in keys])


@router.post("/", response_model=ResponseModel[AgentApiKeyCreatedResponse])
def create_agent_key(payload: AgentApiKeyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key, raw = AgentKeyService.create_key(db, current_user, payload.name, payload.space_id)
    record_audit_log(
        db,
        action="create_agent_key",
        resource=f"agent_key:{key.id}",
        user_id=current_user.id,
        username=current_user.username,
        details={"name": key.name, "space_id": key.space_id},
    )
    data = AgentApiKeyCreatedResponse(
        id=key.id,
        name=key.name,
        key_prefix=key.key_prefix,
        space_id=key.space_id,
        is_active=key.is_active,
        last_used_at=key.last_used_at,
        created_at=key.created_at,
        api_key=raw,
    )
    return ResponseModel(data=data)


@router.delete("/{key_id}", response_model=ResponseModel[dict])
def revoke_agent_key(key_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key = AgentKeyService.revoke_key(db, current_user, key_id)
    record_audit_log(
        db,
        action="revoke_agent_key",
        resource=f"agent_key:{key.id}",
        user_id=current_user.id,
        username=current_user.username,
        details={"name": key.name},
    )
    return ResponseModel(data={"message": "Agent API Key 已撤销"})
