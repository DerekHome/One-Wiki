"""add agent api keys

Revision ID: b7c1a2d90e11
Revises: 3fe547346874
Create Date: 2026-09-16 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c1a2d90e11"
down_revision: Union[str, None] = "3fe547346874"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_api_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("key_prefix", sa.String(length=16), nullable=False),
        sa.Column("hashed_key", sa.String(length=64), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("space_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["space_id"], ["spaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_api_keys_id"), "agent_api_keys", ["id"], unique=False)
    op.create_index(op.f("ix_agent_api_keys_key_prefix"), "agent_api_keys", ["key_prefix"], unique=False)
    op.create_index(op.f("ix_agent_api_keys_hashed_key"), "agent_api_keys", ["hashed_key"], unique=True)
    op.create_index(op.f("ix_agent_api_keys_owner_user_id"), "agent_api_keys", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_agent_api_keys_space_id"), "agent_api_keys", ["space_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_api_keys_space_id"), table_name="agent_api_keys")
    op.drop_index(op.f("ix_agent_api_keys_owner_user_id"), table_name="agent_api_keys")
    op.drop_index(op.f("ix_agent_api_keys_hashed_key"), table_name="agent_api_keys")
    op.drop_index(op.f("ix_agent_api_keys_key_prefix"), table_name="agent_api_keys")
    op.drop_index(op.f("ix_agent_api_keys_id"), table_name="agent_api_keys")
    op.drop_table("agent_api_keys")
