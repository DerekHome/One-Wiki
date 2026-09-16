import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import check_space_permission
from app.models.entities import AgentApiKey, User
from app.schemas.agent_key import AgentApiKeyCreatedResponse, AgentApiKeyResponse

KEY_PREFIX = "kck_"

DEFAULT_AGENT_PERMISSIONS = [
    "list_spaces",
    "search",
    "read",
    "related",
    "versions",
    "attachments",
]
VALID_AGENT_PERMISSIONS: Set[str] = set(DEFAULT_AGENT_PERMISSIONS)


class AgentKeyService:
    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_key() -> str:
        return f"{KEY_PREFIX}{secrets.token_hex(24)}"

    @staticmethod
    def resolve_space_ids(key: AgentApiKey) -> List[int]:
        raw = key.space_ids if isinstance(key.space_ids, list) else []
        ids: List[int] = []
        for item in raw:
            try:
                value = int(item)
            except (TypeError, ValueError):
                continue
            if value not in ids:
                ids.append(value)
        if not ids and key.space_id:
            ids = [key.space_id]
        return ids

    @staticmethod
    def resolve_permissions(key: AgentApiKey) -> List[str]:
        raw = key.permissions
        if raw is None:
            return list(DEFAULT_AGENT_PERMISSIONS)
        if not isinstance(raw, list):
            return list(DEFAULT_AGENT_PERMISSIONS)
        return [item for item in raw if item in VALID_AGENT_PERMISSIONS]

    @staticmethod
    def validate_permissions(permissions: Optional[List[str]]) -> List[str]:
        if permissions is None:
            return list(DEFAULT_AGENT_PERMISSIONS)
        unknown = [item for item in permissions if item not in VALID_AGENT_PERMISSIONS]
        if unknown:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_AGENT_PERMISSION", "message": f"不支持的 Agent 能力: {', '.join(unknown)}"},
            )
        return [item for item in permissions if item in VALID_AGENT_PERMISSIONS]

    @staticmethod
    def coerce_space_ids(space_id: Optional[int], space_ids: Optional[List[int]]) -> List[int]:
        if space_ids:
            values = space_ids
        elif space_id is not None:
            values = [space_id]
        else:
            values = []
        result: List[int] = []
        for item in values:
            value = int(item)
            if value not in result:
                result.append(value)
        return result

    @staticmethod
    def ensure_space_access(db: Session, owner: User, space_ids: List[int]) -> None:
        for space_id in space_ids:
            check_space_permission(db, space_id, owner, "viewer")

    @staticmethod
    def apply_space_fields(record: AgentApiKey, space_ids: List[int]) -> None:
        record.space_ids = space_ids
        record.space_id = space_ids[0] if len(space_ids) == 1 else None

    @staticmethod
    def attach_agent_principal(user: User, key: AgentApiKey) -> User:
        space_ids = AgentKeyService.resolve_space_ids(key)
        user.actor_type = "agent"
        user.agent_key_id = key.id
        user.agent_key_name = key.name
        user.agent_description = key.description
        user.agent_space_id = space_ids[0] if len(space_ids) == 1 else None
        user.agent_space_ids = space_ids or None
        user.agent_permissions = set(AgentKeyService.resolve_permissions(key))
        return user

    @staticmethod
    def to_response(key: AgentApiKey, owner_username: Optional[str] = None, api_key: Optional[str] = None):
        payload: Dict[str, Any] = {
            "id": key.id,
            "name": key.name,
            "description": key.description,
            "key_prefix": key.key_prefix,
            "space_id": key.space_id,
            "space_ids": AgentKeyService.resolve_space_ids(key),
            "permissions": AgentKeyService.resolve_permissions(key),
            "owner_user_id": key.owner_user_id,
            "owner_username": owner_username,
            "is_active": key.is_active,
            "last_used_at": key.last_used_at,
            "created_at": key.created_at,
        }
        if api_key is not None:
            return AgentApiKeyCreatedResponse(**payload, api_key=api_key)
        return AgentApiKeyResponse(**payload)

    @staticmethod
    def authenticate(db: Session, raw_key: str) -> User:
        digest = AgentKeyService.hash_key(raw_key)
        key = db.query(AgentApiKey).filter(AgentApiKey.hashed_key == digest, AgentApiKey.is_active == True).first()
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_AGENT_KEY", "message": "Agent API Key 无效或已撤销"},
            )
        user = db.query(User).filter(User.id == key.owner_user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_AGENT_KEY", "message": "Agent API Key 绑定的账户不可用"},
            )
        key.last_used_at = datetime.now(timezone.utc)
        db.add(key)
        db.commit()
        db.refresh(user)
        db.refresh(key)
        return AgentKeyService.attach_agent_principal(user, key)

    @staticmethod
    def create_key(
        db: Session,
        owner: User,
        name: str,
        space_id: Optional[int] = None,
        space_ids: Optional[List[int]] = None,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
    ) -> Tuple[AgentApiKey, str]:
        resolved_spaces = AgentKeyService.coerce_space_ids(space_id, space_ids)
        AgentKeyService.ensure_space_access(db, owner, resolved_spaces)
        resolved_permissions = AgentKeyService.validate_permissions(permissions)
        raw_key = AgentKeyService.generate_key()
        record = AgentApiKey(
            name=name.strip(),
            description=(description or "").strip() or None,
            key_prefix=raw_key[:12],
            hashed_key=AgentKeyService.hash_key(raw_key),
            owner_user_id=owner.id,
            is_active=True,
            permissions=resolved_permissions,
        )
        AgentKeyService.apply_space_fields(record, resolved_spaces)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record, raw_key

    @staticmethod
    def get_managed_key(db: Session, owner: User, key_id: int) -> AgentApiKey:
        key = db.query(AgentApiKey).filter(AgentApiKey.id == key_id).first()
        if not key:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Agent API Key 不存在"})
        if key.owner_user_id != owner.id and owner.role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权管理该 Agent 凭证"})
        return key

    @staticmethod
    def update_key(
        db: Session,
        owner: User,
        key_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        space_ids: Optional[List[int]] = None,
        permissions: Optional[List[str]] = None,
    ) -> AgentApiKey:
        key = AgentKeyService.get_managed_key(db, owner, key_id)
        if name is not None:
            key.name = name.strip()
        if description is not None:
            key.description = description.strip() or None
        if space_ids is not None:
            resolved_spaces = AgentKeyService.coerce_space_ids(None, space_ids)
            AgentKeyService.ensure_space_access(db, owner, resolved_spaces)
            AgentKeyService.apply_space_fields(key, resolved_spaces)
        if permissions is not None:
            key.permissions = AgentKeyService.validate_permissions(permissions)
        db.commit()
        db.refresh(key)
        return key

    @staticmethod
    def list_keys(db: Session, owner: User) -> List[AgentApiKey]:
        query = db.query(AgentApiKey).filter(AgentApiKey.owner_user_id == owner.id)
        if owner.role in ["owner", "admin"]:
            query = db.query(AgentApiKey)
        return query.order_by(AgentApiKey.created_at.desc()).all()

    @staticmethod
    def owner_usernames(db: Session, keys: List[AgentApiKey]) -> Dict[int, str]:
        owner_ids = {key.owner_user_id for key in keys}
        if not owner_ids:
            return {}
        rows = db.query(User.id, User.username).filter(User.id.in_(owner_ids)).all()
        return {row.id: row.username for row in rows}

    @staticmethod
    def revoke_key(db: Session, owner: User, key_id: int) -> AgentApiKey:
        key = AgentKeyService.get_managed_key(db, owner, key_id)
        key.is_active = False
        key.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(key)
        return key
