"""agent key profile and permissions

Revision ID: c8d3e4f01a22
Revises: b7c1a2d90e11
Create Date: 2026-09-16 12:40:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8d3e4f01a22"
down_revision: Union[str, None] = "b7c1a2d90e11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("agent_api_keys", sa.Column("description", sa.String(length=512), nullable=True))
    op.add_column("agent_api_keys", sa.Column("space_ids", sa.JSON(), nullable=True))
    op.add_column("agent_api_keys", sa.Column("permissions", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("agent_api_keys", "permissions")
    op.drop_column("agent_api_keys", "space_ids")
    op.drop_column("agent_api_keys", "description")
