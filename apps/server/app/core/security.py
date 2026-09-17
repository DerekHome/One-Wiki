import hashlib
import os
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)

def get_password_hash(password: str) -> str:
    """使用 Python 标准库 scrypt，避免可预测的快速哈希被暴力破解。"""
    salt = os.urandom(16)
    hashed = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${hashed.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("scrypt$"):
        try:
            _, salt_hex, original_hash = hashed_password.split("$", 2)
            new_hash = hashlib.scrypt(
                plain_password.encode("utf-8"), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1
            ).hex()
            return hmac.compare_digest(original_hash, new_hash)
        except (ValueError, TypeError):
            return False
    # 兼容旧版 salt$sha256 格式；登录成功后由 auth 路由自动升级。
    if "$" not in hashed_password:
        return False
    salt, original_hash = hashed_password.split("$", 1)
    new_hash = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
    return hmac.compare_digest(original_hash, new_hash)


def password_needs_rehash(hashed_password: str) -> bool:
    return not hashed_password.startswith("scrypt$")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user_optional(
    token_oauth: Optional[str] = Depends(oauth2_scheme),
    token_bearer: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: Session = Depends(get_db)
):
    from app.models.entities import User
    from app.services.agent_key_service import KEY_PREFIX, AgentKeyService

    token = token_bearer.credentials if token_bearer else token_oauth
    if not token:
        return None
    if token.startswith(KEY_PREFIX):
        return AgentKeyService.authenticate(db, token)
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    token_stamp = payload.get("sst")
    current_stamp = int(getattr(user, "security_stamp", 0) or 0)
    if token_stamp is None:
        if current_stamp != 0:
            return None
    elif int(token_stamp) != current_stamp:
        return None
    user.actor_type = "human"
    return user

def get_current_user(
    request: Request,
    current_user = Depends(get_current_user_optional)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "未登录或凭证已失效"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "USER_INACTIVE", "message": "账户已被禁用"}
        )
    if getattr(current_user, "actor_type", None) == "agent":
        path = request.url.path.rstrip("/")
        if path != "/api/v1/agent" and not path.startswith("/api/v1/agent/"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "AGENT_READ_ONLY", "message": "Agent 凭证只能调用 /api/v1/agent 只读知识接口"},
            )
    return current_user
