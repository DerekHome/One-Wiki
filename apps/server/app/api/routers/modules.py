from fastapi import APIRouter, Depends, Body
from app.models.entities import User
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.permissions import check_admin
from app.core.modules.registry import module_registry
from typing import List, Dict, Any

router = APIRouter()

@router.get("/")
def list_modules(current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    return ResponseModel(data=module_registry.list_modules())

@router.post("/{module_id}/enable")
def enable_module(module_id: str, current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    module_registry.enable(module_id)
    return ResponseModel(data={"message": f"模块 {module_id} 已启用", "status": "enabled"})

@router.post("/{module_id}/disable")
def disable_module(module_id: str, current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    module_registry.disable(module_id)
    return ResponseModel(data={"message": f"模块 {module_id} 已禁用", "status": "disabled"})

@router.put("/{module_id}/config")
def update_module_config(module_id: str, config: Dict[str, Any] = Body(...), current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    module_registry.update_config(module_id, config)
    return ResponseModel(data={"message": f"模块 {module_id} 配置已更新", "config": config})
