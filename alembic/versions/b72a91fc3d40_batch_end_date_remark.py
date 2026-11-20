"""Store batch end date remarks and allow same-day batches.

Revision ID: b72a91fc3d40
Revises: 0ce4be9dbe23
Create Date: 2026-11-20
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b72a91fc3d40"
down_revision: str | None = "0ce4be9dbe23"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "batches",
        sa.Column("end_date_remark", sa.Text(), nullable=True),
    )
    op.drop_constraint("ck_batch_dates", "batches", type_="check")
    op.create_check_constraint(
        "ck_batch_dates", "batches", "end_date >= start_date"
    )


def downgrade() -> None:
    op.drop_constraint("ck_batch_dates", "batches", type_="check")
    op.create_check_constraint(
        "ck_batch_dates", "batches", "end_date > start_date"
    )
    op.drop_column("batches", "end_date_remark")
