from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import User
from app.schemas.common import ResponseModel
from app.schemas.agent_key import AgentApiKeyCreate, AgentApiKeyCreatedResponse, AgentApiKeyResponse, AgentApiKeyUpdate
from app.core.security import get_current_user
from app.core.audit import record_audit_log
from app.services.agent_key_service import AgentKeyService
from typing import List

router = APIRouter()


@router.get("/", response_model=ResponseModel[List[AgentApiKeyResponse]])
def list_agent_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = AgentKeyService.list_keys(db, current_user)
    owners = AgentKeyService.owner_usernames(db, keys)
    return ResponseModel(data=[AgentKeyService.to_response(key, owners.get(key.owner_user_id)) for key in keys])


@router.post("/", response_model=ResponseModel[AgentApiKeyCreatedResponse])
def create_agent_key(payload: AgentApiKeyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key, raw = AgentKeyService.create_key(
        db,
        current_user,
        payload.name,
        space_id=payload.space_id,
        space_ids=payload.space_ids,
        description=payload.description,
        permissions=payload.permissions,
    )
    record_audit_log(
        db,
        action="create_agent_key",
        resource=f"agent_key:{key.id}",
        user_id=current_user.id,
        username=current_user.username,
        details={
            "name": key.name,
            "space_ids": AgentKeyService.resolve_space_ids(key),
            "permissions": AgentKeyService.resolve_permissions(key),
        },
    )
    return ResponseModel(data=AgentKeyService.to_response(key, current_user.username, api_key=raw))


@router.put("/{key_id}", response_model=ResponseModel[AgentApiKeyResponse])
def update_agent_key(
    key_id: int,
    payload: AgentApiKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    key = AgentKeyService.update_key(
        db,
        current_user,
        key_id,
        name=payload.name,
        description=payload.description,
        space_ids=payload.space_ids,
        permissions=payload.permissions,
    )
    record_audit_log(
        db,
        action="update_agent_key",
        resource=f"agent_key:{key.id}",
        user_id=current_user.id,
        username=current_user.username,
        details={
            "name": key.name,
            "space_ids": AgentKeyService.resolve_space_ids(key),
            "permissions": AgentKeyService.resolve_permissions(key),
        },
    )
    owners = AgentKeyService.owner_usernames(db, [key])
    return ResponseModel(data=AgentKeyService.to_response(key, owners.get(key.owner_user_id)))


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
