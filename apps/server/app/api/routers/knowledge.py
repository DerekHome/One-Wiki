from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User, Knowledge
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse, KnowledgeVersionResponse, VersionDiffResponse
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.permissions import check_space_permission, can_access_knowledge
from app.services.knowledge_service import KnowledgeService
from app.core.audit import record_audit_log
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=ResponseModel[List[KnowledgeResponse]])
def list_knowledge(
    space_id: Optional[int] = None,
    status: Optional[str] = Query(None, description="draft / published / archived；空则按权限返回"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Knowledge).filter(Knowledge.is_deleted == False)
    if space_id:
        check_space_permission(db, space_id, current_user, "viewer")
        query = query.filter(Knowledge.space_id == space_id)
        from app.core.permissions import get_space_role, ROLE_LEVELS
        space_role = get_space_role(db, space_id, current_user)
        can_see_drafts = ROLE_LEVELS.get(space_role, 0) >= ROLE_LEVELS["editor"] or current_user.role in ["owner", "admin"]
        if status:
            query = query.filter(Knowledge.status == status)
        elif not can_see_drafts:
            query = query.filter(Knowledge.status == "published")
    else:
        query = query.filter(Knowledge.status == "published")
        if status:
            query = query.filter(Knowledge.status == status)
    items = query.order_by(Knowledge.updated_at.desc()).all()
    results = []
    for k in items:
        if can_access_knowledge(db, k, current_user, "read"):
            resp = KnowledgeResponse.model_validate(k)
            resp.tags = KnowledgeService._get_tags(db, k.id)
            results.append(resp)
    return ResponseModel(data=results)

@router.post("/", response_model=ResponseModel[KnowledgeResponse])
def create_knowledge(data: KnowledgeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_space_permission(db, data.space_id, current_user, "editor")
    k = KnowledgeService.create_knowledge(db, data, current_user)
    record_audit_log(db, action="create_knowledge", resource=f"knowledge:{k.id}", user_id=current_user.id, username=current_user.username, details={"title": k.title, "space_id": k.space_id})
    resp = KnowledgeResponse.model_validate(k)
    resp.tags = KnowledgeService._get_tags(db, k.id)
    return ResponseModel(data=resp)

@router.post("/import-file", response_model=ResponseModel[KnowledgeResponse])
async def import_file(
    space_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_space_permission(db, space_id, current_user, "editor")
    k = await KnowledgeService.import_file(db, space_id, file, current_user)
    record_audit_log(
        db,
        action="import_file",
        resource=f"knowledge:{k.id}",
        user_id=current_user.id,
        username=current_user.username,
        details={"filename": file.filename, "space_id": space_id, "title": k.title}
    )
    resp = KnowledgeResponse.model_validate(k)
    resp.tags = KnowledgeService._get_tags(db, k.id)
    return ResponseModel(data=resp)

@router.get("/{knowledge_id}", response_model=ResponseModel[KnowledgeResponse])
def get_knowledge(knowledge_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, knowledge_id)
    if not can_access_knowledge(db, k, current_user, "read"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权查看此知识"})
    resp = KnowledgeResponse.model_validate(k)
    resp.tags = KnowledgeService._get_tags(db, k.id)
    return ResponseModel(data=resp)

@router.put("/{knowledge_id}", response_model=ResponseModel[KnowledgeResponse])
def update_knowledge(knowledge_id: int, data: KnowledgeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, knowledge_id)
    if not can_access_knowledge(db, k, current_user, "edit"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权编辑此知识"})
    updated = KnowledgeService.update_knowledge(db, knowledge_id, data, current_user)
    record_audit_log(db, action="update_knowledge", resource=f"knowledge:{k.id}", user_id=current_user.id, username=current_user.username, details={"title": updated.title})
    resp = KnowledgeResponse.model_validate(updated)
    resp.tags = KnowledgeService._get_tags(db, updated.id)
    return ResponseModel(data=resp)

@router.delete("/{knowledge_id}", response_model=ResponseModel[dict])
def delete_knowledge(knowledge_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, knowledge_id)
    if not can_access_knowledge(db, k, current_user, "delete"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权删除此知识"})
    KnowledgeService.delete_knowledge(db, knowledge_id)
    record_audit_log(db, action="delete_knowledge", resource=f"knowledge:{knowledge_id}", user_id=current_user.id, username=current_user.username)
    return ResponseModel(data={"message": "知识已删除"})

@router.get("/{knowledge_id}/versions", response_model=ResponseModel[List[KnowledgeVersionResponse]])
def list_versions(knowledge_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, knowledge_id)
    if not can_access_knowledge(db, k, current_user, "read"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权查看版本历史"})
    versions = KnowledgeService.list_versions(db, knowledge_id)
    return ResponseModel(data=[KnowledgeVersionResponse.model_validate(v) for v in versions])

@router.get("/{knowledge_id}/versions/{version_number}", response_model=ResponseModel[KnowledgeVersionResponse])
def get_version(knowledge_id: int, version_number: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, knowledge_id)
    if not can_access_knowledge(db, k, current_user, "read"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权查看该版本"})
    v = KnowledgeService.get_version(db, knowledge_id, version_number)
    return ResponseModel(data=KnowledgeVersionResponse.model_validate(v))

@router.get("/{knowledge_id}/diff", response_model=ResponseModel[VersionDiffResponse])
def compare_versions(
    knowledge_id: int,
    v_from: int = Query(..., ge=1),
    v_to: int = Query(..., ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    k = KnowledgeService.get_knowledge(db, knowledge_id)
    if not can_access_knowledge(db, k, current_user, "read"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权比较版本"})
    diff_data = KnowledgeService.compare_versions(db, knowledge_id, v_from, v_to)
    return ResponseModel(data=VersionDiffResponse(**diff_data))

@router.post("/{knowledge_id}/restore/{version_number}", response_model=ResponseModel[KnowledgeResponse])
def restore_version(knowledge_id: int, version_number: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    k = KnowledgeService.get_knowledge(db, knowledge_id)
    if not can_access_knowledge(db, k, current_user, "edit"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权恢复历史版本"})
    restored = KnowledgeService.restore_version(db, knowledge_id, version_number, current_user)
    record_audit_log(db, action="restore_version", resource=f"knowledge:{knowledge_id}", user_id=current_user.id, username=current_user.username, details={"target_version": version_number})
    resp = KnowledgeResponse.model_validate(restored)
    resp.tags = KnowledgeService._get_tags(db, restored.id)
    return ResponseModel(data=resp)
