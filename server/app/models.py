from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def uuid_str() -> str:
    return str(uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    display_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(32), default="reader")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Group(Base):
    __tablename__ = "groups"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class GroupMember(Base):
    __tablename__ = "group_members"
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class GroupPermission(Base):
    __tablename__ = "group_permissions"
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    permission: Mapped[str] = mapped_column(String(80), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class SessionToken(Base):
    __tablename__ = "session_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("topics.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class KnowledgePage(Base):
    __tablename__ = "knowledge_pages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    topic_id: Mapped[str | None] = mapped_column(ForeignKey("topics.id"), nullable=True, index=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    current_version: Mapped[int] = mapped_column(Integer, default=0)
    review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class PageVersion(Base):
    __tablename__ = "page_versions"
    __table_args__ = (UniqueConstraint("page_id", "version_no", name="uq_page_version"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    page_id: Mapped[str] = mapped_column(ForeignKey("knowledge_pages.id"), index=True)
    version_no: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    change_note: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class PageTag(Base):
    __tablename__ = "page_tags"
    page_id: Mapped[str] = mapped_column(ForeignKey("knowledge_pages.id"), primary_key=True)
    tag_id: Mapped[str] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class Favorite(Base):
    __tablename__ = "favorites"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    page_id: Mapped[str] = mapped_column(ForeignKey("knowledge_pages.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class FileAsset(Base):
    __tablename__ = "file_assets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    storage_key: Mapped[str] = mapped_column(String(512), unique=True)
    original_name: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str] = mapped_column(String(255), default="application/octet-stream")
    size: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    page_id: Mapped[str | None] = mapped_column(ForeignKey("knowledge_pages.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
