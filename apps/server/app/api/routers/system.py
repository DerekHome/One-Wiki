import os
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import get_db
from app.models.entities import User, Space, Knowledge, KnowledgeVersion, Attachment, AuditLog
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.permissions import check_admin
from app.core.config import settings
from typing import Dict, Any

router = APIRouter()

# 模拟/持久化系统偏好配置
_system_settings = {
    "site_name": "企业知识中心 (Knowledge Hub)",
    "storage_type": "local",
    "storage_path": settings.UPLOAD_DIR,
    "max_upload_size_mb": 50,
    "allowed_extensions": [".md", ".markdown", ".html", ".htm", ".png", ".jpg", ".pdf", ".zip"],
    "allow_registration": True,
    "default_space_visibility": "internal",
    "jwt_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
}

@router.get("/stats")
def get_system_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)

    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    total_spaces = db.query(func.count(Space.id)).filter(Space.is_deleted == False).scalar() or 0
    total_knowledge = db.query(func.count(Knowledge.id)).filter(Knowledge.is_deleted == False).scalar() or 0
    total_versions = db.query(func.count(KnowledgeVersion.id)).scalar() or 0
    total_attachments = db.query(func.count(Attachment.id)).scalar() or 0
    total_storage_bytes = db.query(func.sum(Attachment.size)).scalar() or 0
    total_audit_logs = db.query(func.count(AuditLog.id)).scalar() or 0

    return ResponseModel(data={
        "total_users": total_users,
        "active_users": active_users,
        "total_spaces": total_spaces,
        "total_knowledge": total_knowledge,
        "total_versions": total_versions,
        "total_attachments": total_attachments,
        "storage_size_bytes": total_storage_bytes,
        "storage_size_mb": round(total_storage_bytes / (1024 * 1024), 2),
        "total_audit_logs": total_audit_logs
    })

@router.get("/settings")
def get_system_settings(current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    return ResponseModel(data=_system_settings)

@router.put("/settings")
def update_system_settings(payload: Dict[str, Any] = Body(...), current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    _system_settings.update(payload)
    return ResponseModel(data=_system_settings)

@router.get("/roles-matrix")
def get_roles_matrix(current_user: User = Depends(get_current_user)):
    # 返回企业知识中心规范的 RBAC 角色能力矩阵
    matrix = [
        {
            "role": "owner",
            "name": "超级所有者",
            "description": "拥有系统最高控制权，可管理全局配置、删除空间、分配系统角色",
            "permissions": ["全系统配置", "用户管理", "模块管理", "所有空间完全控制", "全量审计查看"]
        },
        {
            "role": "admin",
            "name": "系统管理员",
            "description": "负责空间调配、成员授权审批、操作日志审计与模块监控",
            "permissions": ["用户启停", "创建空间", "空间成员调度", "模块启停", "审计检索"]
        },
        {
            "role": "editor",
            "name": "知识编辑者",
            "description": "具有知识创作、版本更新、富文本编写及附件上传权",
            "permissions": ["创建知识", "更新并生成新版本", "恢复历史版本", "上传附件", "文档导出"]
        },
        {
            "role": "viewer",
            "name": "受限只读者",
            "description": "仅具备公开与授权空间内的知识浏览与检索权限，写操作受限",
            "permissions": ["浏览知识正文", "查看版本历史", "下载附件", "执行全文搜索"]
        }
    ]
    return ResponseModel(data=matrix)
