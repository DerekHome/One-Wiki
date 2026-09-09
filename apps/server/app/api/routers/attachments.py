from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User, Knowledge
from app.schemas.attachment import AttachmentResponse
from app.schemas.common import ResponseModel
from app.core.security import get_current_user
from app.core.permissions import can_access_knowledge
from app.services.attachment_service import AttachmentService
from app.services.knowledge_service import KnowledgeService
from app.core.audit import record_audit_log
from typing import List

router = APIRouter()

@router.post("/{knowledge_id}", response_model=ResponseModel[AttachmentResponse])
async def upload_attachment(
    knowledge_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    k = KnowledgeService.get_knowledge(db, knowledge_id)
    if not can_access_knowledge(db, k, current_user, "edit"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权向该知识上传附件"})
    att = await AttachmentService.upload_attachment(db, knowledge_id, file, current_user)
    record_audit_log(db, action="upload_attachment", resource=f"attachment:{att.id}", user_id=current_user.id, username=current_user.username, details={"filename": att.filename, "size": att.size})
    return ResponseModel(data=AttachmentResponse.model_validate(att))

@router.get("/knowledge/{knowledge_id}", response_model=ResponseModel[List[AttachmentResponse]])
def list_attachments(
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    k = KnowledgeService.get_knowledge(db, knowledge_id)
    if not can_access_knowledge(db, k, current_user, "read"):
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权查看该知识附件"})
    atts = AttachmentService.list_attachments(db, knowledge_id)
    return ResponseModel(data=[AttachmentResponse.model_validate(a) for a in atts])

@router.get("/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    att = AttachmentService.get_attachment(db, attachment_id)
    if att.knowledge_id:
        k = KnowledgeService.get_knowledge(db, att.knowledge_id)
        if not can_access_knowledge(db, k, current_user, "read"):
            raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权下载该附件"})
    record_audit_log(db, action="download_attachment", resource=f"attachment:{att.id}", user_id=current_user.id, username=current_user.username, details={"filename": att.filename})
    return FileResponse(path=att.storage_path, filename=att.filename, media_type=att.mime_type or "application/octet-stream")

@router.delete("/{attachment_id}", response_model=ResponseModel[dict])
def delete_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    att = AttachmentService.get_attachment(db, attachment_id)
    if att.knowledge_id:
        k = KnowledgeService.get_knowledge(db, att.knowledge_id)
        if not can_access_knowledge(db, k, current_user, "edit"):
            raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权删除该附件"})
    AttachmentService.delete_attachment(db, attachment_id)
    record_audit_log(db, action="delete_attachment", resource=f"attachment:{attachment_id}", user_id=current_user.id, username=current_user.username)
    return ResponseModel(data={"message": "附件已删除"})
