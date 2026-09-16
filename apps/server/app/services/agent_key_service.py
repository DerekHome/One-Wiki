import hashlib
import secrets
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import check_space_permission
from app.models.entities import AgentApiKey, User

KEY_PREFIX = "kck_"


class AgentKeyService:
    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_key() -> str:
        return f"{KEY_PREFIX}{secrets.token_hex(24)}"

    @staticmethod
    def attach_agent_principal(user: User, key: AgentApiKey) -> User:
        user.actor_type = "agent"
        user.agent_key_id = key.id
        user.agent_key_name = key.name
        user.agent_space_id = key.space_id
        return user

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
    def create_key(db: Session, owner: User, name: str, space_id: Optional[int] = None) -> Tuple[AgentApiKey, str]:
        if space_id is not None:
            check_space_permission(db, space_id, owner, "viewer")
        raw_key = AgentKeyService.generate_key()
        record = AgentApiKey(
            name=name.strip(),
            key_prefix=raw_key[:12],
            hashed_key=AgentKeyService.hash_key(raw_key),
            owner_user_id=owner.id,
            space_id=space_id,
            is_active=True,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record, raw_key

    @staticmethod
    def list_keys(db: Session, owner: User) -> List[AgentApiKey]:
        query = db.query(AgentApiKey).filter(AgentApiKey.owner_user_id == owner.id)
        if owner.role in ["owner", "admin"]:
            query = db.query(AgentApiKey)
        return query.order_by(AgentApiKey.created_at.desc()).all()

    @staticmethod
    def revoke_key(db: Session, owner: User, key_id: int) -> AgentApiKey:
        key = db.query(AgentApiKey).filter(AgentApiKey.id == key_id).first()
        if not key:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Agent API Key 不存在"})
        if key.owner_user_id != owner.id and owner.role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权撤销该 Key"})
        key.is_active = False
        key.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(key)
        return key
