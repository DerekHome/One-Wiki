from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.entities import Topic, Space
from app.schemas.topic import TopicCreate, TopicUpdate
from typing import List

class TopicService:
    @staticmethod
    def create_topic(db: Session, data: TopicCreate) -> Topic:
        space = db.query(Space).filter(Space.id == data.space_id, Space.is_deleted == False).first()
        if not space:
            raise HTTPException(status_code=404, detail={"code": "SPACE_NOT_FOUND", "message": "所属空间不存在"})

        topic = Topic(
            space_id=data.space_id,
            name=data.name,
            description=data.description,
            sort_order=data.sort_order or 0,
            is_deleted=False
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)
        return topic

    @staticmethod
    def list_topics_by_space(db: Session, space_id: int) -> List[Topic]:
        return db.query(Topic).filter(
            Topic.space_id == space_id,
            Topic.is_deleted == False
        ).order_by(Topic.sort_order.asc(), Topic.id.asc()).all()

    @staticmethod
    def get_topic(db: Session, topic_id: int) -> Topic:
        topic = db.query(Topic).filter(Topic.id == topic_id, Topic.is_deleted == False).first()
        if not topic:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "专题不存在"})
        return topic

    @staticmethod
    def update_topic(db: Session, topic_id: int, data: TopicUpdate) -> Topic:
        topic = TopicService.get_topic(db, topic_id)
        if data.name is not None:
            topic.name = data.name
        if data.description is not None:
            topic.description = data.description
        if data.sort_order is not None:
            topic.sort_order = data.sort_order
        db.commit()
        db.refresh(topic)
        return topic

    @staticmethod
    def delete_topic(db: Session, topic_id: int):
        topic = TopicService.get_topic(db, topic_id)
        topic.is_deleted = True
        db.commit()
