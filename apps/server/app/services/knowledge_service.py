import os
import re
import difflib
from html.parser import HTMLParser
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models.entities import Knowledge, KnowledgeVersion, Tag, KnowledgeTag, Space, User
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate
from typing import List, Optional

class SimpleHTMLTitleExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self._in_h1 = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title" and not self.title:
            self._in_title = True
        elif tag.lower() == "h1" and not self.title:
            self._in_h1 = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False
        elif tag.lower() == "h1":
            self._in_h1 = False

    def handle_data(self, data):
        if (self._in_title or self._in_h1) and not self.title:
            text = data.strip()
            if text:
                self.title = text

class KnowledgeService:
    @staticmethod
    def _sync_tags(db: Session, knowledge_id: int, tag_names: List[str]):
        db.query(KnowledgeTag).filter(KnowledgeTag.knowledge_id == knowledge_id).delete()
        for name in tag_names:
            clean_name = name.strip()
            if not clean_name:
                continue
            tag = db.query(Tag).filter(Tag.name == clean_name).first()
            if not tag:
                tag = Tag(name=clean_name)
                db.add(tag)
                db.flush()
            db.add(KnowledgeTag(knowledge_id=knowledge_id, tag_id=tag.id))
        db.flush()

    @staticmethod
    def _get_tags(db: Session, knowledge_id: int) -> List[str]:
        tag_ids = [kt.tag_id for kt in db.query(KnowledgeTag.tag_id).filter(KnowledgeTag.knowledge_id == knowledge_id).all()]
        if not tag_ids:
            return []
        tags = db.query(Tag.name).filter(Tag.id.in_(tag_ids)).all()
        return [t[0] for t in tags]

    @staticmethod
    def create_knowledge(db: Session, data: KnowledgeCreate, user: User) -> Knowledge:
        k = Knowledge(
            space_id=data.space_id,
            title=data.title,
            content=data.content,
            summary=data.summary or (data.content[:150] + "..." if len(data.content) > 150 else data.content),
            knowledge_type=data.knowledge_type or "article",
            status="published",
            owner_id=user.id,
            is_deleted=False,
            published_at=datetime.now(timezone.utc)
        )
        db.add(k)
        db.flush()
        v1 = KnowledgeVersion(
            knowledge_id=k.id,
            version_number=1,
            title=k.title,
            content=k.content,
            change_summary="初始创建并发布",
            created_by=user.id
        )
        db.add(v1)
        db.flush()
        k.current_version_id = v1.id
        if data.tags:
            KnowledgeService._sync_tags(db, k.id, data.tags)
        db.commit()
        db.refresh(k)
        return k

    @staticmethod
    async def import_file(db: Session, space_id: int, file: UploadFile, user: User) -> Knowledge:
        filename = os.path.basename(file.filename or "imported_document")
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".md", ".markdown", ".html", ".htm"]:
            raise HTTPException(
                status_code=400,
                detail={"code": "UNSUPPORTED_FILE_TYPE", "message": f"不支持的文件类型: {ext}，仅支持 .md 和 .html 文件"}
            )

        raw_bytes = await file.read()
        try:
            raw_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                raw_text = raw_bytes.decode("gb18030")
            except UnicodeDecodeError:
                raw_text = raw_bytes.decode("latin-1", errors="replace")

        base_name = os.path.splitext(filename)[0]
        extracted_title = ""
        content_type = "markdown"

        if ext in [".md", ".markdown"]:
            content_type = "markdown"
            # 尝试从 Markdown 第一行提取 # 标题
            title_match = re.search(r'^\s*#\s+(.+)$', raw_text, re.MULTILINE)
            if title_match:
                extracted_title = title_match.group(1).strip()
            content = raw_text
        else:
            content_type = "html"
            parser = SimpleHTMLTitleExtractor()
            try:
                parser.feed(raw_text)
                extracted_title = parser.title
            except Exception:
                pass
            content = raw_text

        final_title = extracted_title if extracted_title else base_name
        # 提炼前150字纯文本作为摘要
        clean_summary = re.sub(r'[#*`<>\[\]\(\)]', '', content)[:150].strip()
        if len(content) > 150:
            clean_summary += "..."

        k = Knowledge(
            space_id=space_id,
            title=final_title,
            content=content,
            content_type=content_type,
            summary=clean_summary,
            knowledge_type="document",
            source_type="file_import",
            source_uri=filename,
            status="published",
            owner_id=user.id,
            is_deleted=False,
            published_at=datetime.now(timezone.utc)
        )
        db.add(k)
        db.flush()

        v1 = KnowledgeVersion(
            knowledge_id=k.id,
            version_number=1,
            title=final_title,
            content=content,
            change_summary=f"自原始文件 [{filename}] 导入生成",
            created_by=user.id
        )
        db.add(v1)
        db.flush()
        k.current_version_id = v1.id

        # 默认附带格式标签
        tag_name = "Markdown" if ext in [".md", ".markdown"] else "HTML"
        KnowledgeService._sync_tags(db, k.id, [tag_name, "文件导入"])

        db.commit()
        db.refresh(k)
        return k

    @staticmethod
    def get_knowledge(db: Session, knowledge_id: int) -> Knowledge:
        k = db.query(Knowledge).filter(Knowledge.id == knowledge_id, Knowledge.is_deleted == False).first()
        if not k:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "知识不存在"})
        return k

    @staticmethod
    def update_knowledge(db: Session, knowledge_id: int, data: KnowledgeUpdate, user: User) -> Knowledge:
        k = KnowledgeService.get_knowledge(db, knowledge_id)
        has_content_change = False
        new_title = data.title if data.title is not None else k.title
        new_content = data.content if data.content is not None else k.content

        if new_title != k.title or new_content != k.content:
            has_content_change = True

        if data.title is not None:
            k.title = data.title
        if data.content is not None:
            k.content = data.content
        if data.summary is not None:
            k.summary = data.summary
        if data.knowledge_type is not None:
            k.knowledge_type = data.knowledge_type
        if data.tags is not None:
            KnowledgeService._sync_tags(db, k.id, data.tags)

        if has_content_change:
            current_max = db.query(KnowledgeVersion.version_number).filter(KnowledgeVersion.knowledge_id == k.id).order_by(KnowledgeVersion.version_number.desc()).first()
            next_ver = (current_max[0] + 1) if current_max else 1
            v_new = KnowledgeVersion(
                knowledge_id=k.id,
                version_number=next_ver,
                title=k.title,
                content=k.content,
                change_summary=data.change_summary or f"更新版本 {next_ver}",
                created_by=user.id
            )
            db.add(v_new)
            db.flush()
            k.current_version_id = v_new.id

        db.commit()
        db.refresh(k)
        return k

    @staticmethod
    def delete_knowledge(db: Session, knowledge_id: int):
        k = KnowledgeService.get_knowledge(db, knowledge_id)
        k.is_deleted = True
        db.commit()

    @staticmethod
    def list_versions(db: Session, knowledge_id: int) -> List[KnowledgeVersion]:
        KnowledgeService.get_knowledge(db, knowledge_id)
        return db.query(KnowledgeVersion).filter(KnowledgeVersion.knowledge_id == knowledge_id).order_by(KnowledgeVersion.version_number.desc()).all()

    @staticmethod
    def get_version(db: Session, knowledge_id: int, version_number: int) -> KnowledgeVersion:
        v = db.query(KnowledgeVersion).filter(
            KnowledgeVersion.knowledge_id == knowledge_id,
            KnowledgeVersion.version_number == version_number
        ).first()
        if not v:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"版本 {version_number} 不存在"})
        return v

    @staticmethod
    def compare_versions(db: Session, knowledge_id: int, v_from: int, v_to: int) -> dict:
        v1 = KnowledgeService.get_version(db, knowledge_id, v_from)
        v2 = KnowledgeService.get_version(db, knowledge_id, v_to)
        diff = list(difflib.unified_diff(
            v1.content.splitlines(keepends=True),
            v2.content.splitlines(keepends=True),
            fromfile=f"Version {v_from}",
            tofile=f"Version {v_to}",
            lineterm=""
        ))
        return {
            "version_from": v_from,
            "version_to": v_to,
            "title_diff": {"from": v1.title, "to": v2.title},
            "content_diff": diff
        }

    @staticmethod
    def restore_version(db: Session, knowledge_id: int, version_number: int, user: User) -> Knowledge:
        target_v = KnowledgeService.get_version(db, knowledge_id, version_number)
        k = KnowledgeService.get_knowledge(db, knowledge_id)
        k.title = target_v.title
        k.content = target_v.content

        current_max = db.query(KnowledgeVersion.version_number).filter(KnowledgeVersion.knowledge_id == k.id).order_by(KnowledgeVersion.version_number.desc()).first()
        next_ver = (current_max[0] + 1) if current_max else 1

        restored_v = KnowledgeVersion(
            knowledge_id=k.id,
            version_number=next_ver,
            title=target_v.title,
            content=target_v.content,
            change_summary=f"回滚自历史版本 {version_number}",
            created_by=user.id
        )
        db.add(restored_v)
        db.flush()
        k.current_version_id = restored_v.id
        db.commit()
        db.refresh(k)
        return k
