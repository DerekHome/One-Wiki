from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User
from app.schemas.user import PublicUserCreate, UserCreate, LoginRequest, TokenResponse, UserResponse
from app.schemas.common import ResponseModel
from app.core.config import settings
from app.core.security import verify_password, create_access_token, get_current_user, get_password_hash, password_needs_rehash
from app.core.rate_limit import login_limiter
from app.services.user_service import UserService
from app.services.system_settings_service import get_cached_settings
from app.core.audit import record_audit_log

router = APIRouter()

@router.post("/register", response_model=ResponseModel[UserResponse])
def register(user_in: PublicUserCreate, db: Session = Depends(get_db)):
    if not get_cached_settings().get("allow_registration", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "REGISTRATION_DISABLED", "message": "公开注册已关闭"},
        )
    # 公开注册永远创建最低权限账户；系统角色只能由受保护的用户管理接口设置。
    user = UserService.create_user(db, UserCreate(username=user_in.username, password=user_in.password, role="viewer"))
    record_audit_log(db, action="register", resource=f"user:{user.id}", user_id=user.id, username=user.username)
    return ResponseModel(data=user)

@router.post("/login", response_model=ResponseModel[TokenResponse])
def login(user_in: LoginRequest, request: Request, db: Session = Depends(get_db)):
    login_limiter.check(request, user_in.username)
    user = UserService.get_by_username(db, user_in.username)
    if not user or not verify_password(user_in.password, user.hashed_password):
        login_limiter.record_failure(request, user_in.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "用户名或密码错误"}
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "USER_INACTIVE", "message": "账户已被禁用"}
        )
    login_limiter.reset(request, user_in.username)
    if password_needs_rehash(user.hashed_password):
        user.hashed_password = get_password_hash(user_in.password)
        db.commit()
        db.refresh(user)
    expire_minutes = int(get_cached_settings().get("jwt_expire_minutes") or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.username, "role": user.role, "uid": user.id, "sst": int(user.security_stamp or 0)},
        expires_delta=timedelta(minutes=expire_minutes),
    )
    record_audit_log(db, action="login", resource=f"user:{user.id}", user_id=user.id, username=user.username)
    return ResponseModel(data=TokenResponse(access_token=token, user=UserResponse.model_validate(user)))

@router.get("/me", response_model=ResponseModel[UserResponse])
def get_current_user_profile(user: User = Depends(get_current_user)):
    return ResponseModel(data=UserResponse.model_validate(user))

@router.post("/logout", response_model=ResponseModel[dict])
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record_audit_log(db, action="logout", resource=f"user:{user.id}", user_id=user.id, username=user.username)
    return ResponseModel(data={"message": "登出成功"})
