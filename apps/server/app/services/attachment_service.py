import os, hashlib, uuid
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models.entities import Attachment, Knowledge, User
from app.core.config import settings
from app.services.system_settings_service import BLOCKED_EXTENSIONS, get_cached_settings

SAFE_INLINE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".txt", ".md", ".markdown", ".csv"}
UNTRUSTED_INLINE_EXTENSIONS = {".html", ".htm", ".svg", ".xml", ".xhtml", ".js", ".mjs"}


class AttachmentService:
    @staticmethod
    def _normalize_filename(filename: str) -> str:
        safe_filename = os.path.basename(filename or "attachment")
        return safe_filename.replace("..", "").replace("/", "").replace("\\", "") or "attachment"

    @staticmethod
    def allowed_extensions() -> set:
        configured = get_cached_settings().get("allowed_extensions") or []
        return {str(ext).lower() for ext in configured}

    @staticmethod
    def max_upload_bytes() -> int:
        size_mb = int(get_cached_settings().get("max_upload_size_mb") or settings.MAX_UPLOAD_SIZE_MB)
        return size_mb * 1024 * 1024

    @staticmethod
    def validate_extension(filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if not ext or ext in BLOCKED_EXTENSIONS:
            raise HTTPException(status_code=422, detail={"code": "FILE_TYPE_DENIED", "message": "不允许的文件类型"})
        allowed = AttachmentService.allowed_extensions()
        if ext not in allowed:
            raise HTTPException(status_code=422, detail={"code": "FILE_TYPE_DENIED", "message": f"仅允许上传: {', '.join(sorted(allowed))}"})
        return ext

    @staticmethod
    def download_headers(filename: str, mime_type: str | None) -> tuple[str, str]:
        ext = Path(filename).suffix.lower()
        if ext in UNTRUSTED_INLINE_EXTENSIONS or ext not in SAFE_INLINE_EXTENSIONS:
            return "application/octet-stream", "attachment"
        return mime_type or "application/octet-stream", "inline"

    @staticmethod
    async def upload_attachment(db: Session, knowledge_id: int, file: UploadFile, user: User) -> Attachment:
        k = db.query(Knowledge).filter(Knowledge.id == knowledge_id, Knowledge.is_deleted == False).first()
        if not k:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "知识不存在"})

        safe_filename = AttachmentService._normalize_filename(file.filename or "attachment")
        AttachmentService.validate_extension(safe_filename)

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        max_bytes = AttachmentService.max_upload_bytes()
        content = await file.read()
        if len(content) > max_bytes:
            size_mb = max(1, max_bytes // (1024 * 1024))
            raise HTTPException(status_code=413, detail={"code": "FILE_TOO_LARGE", "message": f"附件不能超过 {size_mb} MB"})

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
