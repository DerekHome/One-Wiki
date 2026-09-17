"""security stamp, system settings, mysql fulltext

Revision ID: d9e4f5a12b33
Revises: c8d3e4f01a22
Create Date: 2026-09-17 10:50:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d9e4f5a12b33"
down_revision: Union[str, None] = "c8d3e4f01a22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("security_stamp", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    bind = op.get_bind()
    if bind.dialect.name == "mysql":
        op.execute(
            "ALTER TABLE knowledge ADD FULLTEXT INDEX ix_knowledge_fulltext "
            "(title, summary, content) WITH PARSER ngram"
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "mysql":
        op.execute("ALTER TABLE knowledge DROP INDEX ix_knowledge_fulltext")
    op.drop_table("system_settings")
    op.drop_column("users", "security_stamp")
