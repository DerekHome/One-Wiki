import os, hashlib, uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models.entities import Attachment, Knowledge, User
from app.core.config import settings

class AttachmentService:
    @staticmethod
    async def upload_attachment(db: Session, knowledge_id: int, file: UploadFile, user: User) -> Attachment:
        k = db.query(Knowledge).filter(Knowledge.id == knowledge_id, Knowledge.is_deleted == False).first()
        if not k:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "知识不存在"})

        safe_filename = os.path.basename(file.filename or "attachment")
        safe_filename = safe_filename.replace("..", "").replace("/", "").replace("\\", "")

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        content = await file.read()
        if len(content) > max_bytes:
            raise HTTPException(status_code=413, detail={"code": "FILE_TOO_LARGE", "message": f"附件不能超过 {settings.MAX_UPLOAD_SIZE_MB} MB"})

        unique_name = f"att_{k.id}_{uuid.uuid4().hex}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
        checksum = hashlib.sha256(content).hexdigest()
        size = len(content)

        try:
            with open(file_path, "wb") as f:
                f.write(content)
            att = Attachment(
                knowledge_id=knowledge_id,
                filename=safe_filename,
                mime_type=file.content_type or "application/octet-stream",
                size=size,
                storage_path=file_path,
                checksum=checksum,
                created_by=user.id
            )
            db.add(att)
            db.commit()
            db.refresh(att)
            return att
        except Exception:
            db.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

    @staticmethod
    def get_attachment(db: Session, attachment_id: int) -> Attachment:
        att = db.query(Attachment).filter(Attachment.id == attachment_id).first()
        if not att:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "附件不存在"})
        if not os.path.exists(att.storage_path):
            raise HTTPException(status_code=404, detail={"code": "FILE_MISSING", "message": "物理文件丢失"})
        return att

    @staticmethod
    def list_attachments(db: Session, knowledge_id: int) -> list:
        return db.query(Attachment).filter(Attachment.knowledge_id == knowledge_id).all()

    @staticmethod
    def delete_attachment(db: Session, attachment_id: int):
        att = AttachmentService.get_attachment(db, attachment_id)
        if os.path.exists(att.storage_path):
            try:
                os.remove(att.storage_path)
            except Exception:
                pass
        db.delete(att)
        db.commit()
