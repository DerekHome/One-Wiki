from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.entities import Tag, KnowledgeTag, Knowledge
from app.schemas.tag import TagCreate
from typing import List

class TagService:
    @staticmethod
    def create_tag(db: Session, data: TagCreate) -> Tag:
        clean = data.name.strip()
        existing = db.query(Tag).filter(Tag.name == clean).first()
        if existing:
            return existing
        tag = Tag(name=clean)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    @staticmethod
    def list_tags(db: Session) -> List[Tag]:
        return db.query(Tag).order_by(Tag.name.asc()).all()

    @staticmethod
    def delete_tag(db: Session, tag_id: int):
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "标签不存在"})
        db.query(KnowledgeTag).filter(KnowledgeTag.tag_id == tag_id).delete()
        db.delete(tag)
        db.commit()
