"""Add soft-delete support to batches.

Revision ID: d2c6b716a8e1
Revises: c1d09e4a7b32
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d2c6b716a8e1"
down_revision: Union[str, None] = "c1d09e4a7b32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "batches",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("batches", "is_active")
