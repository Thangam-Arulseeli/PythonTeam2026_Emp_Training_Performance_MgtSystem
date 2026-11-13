"""Remove the stored normalized course duration.

Revision ID: f8a4c1d7602b
Revises: e4f18c720a64
Create Date: 2026-11-13
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f8a4c1d7602b"
down_revision: str | None = "e4f18c720a64"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_course_duration_hours_positive", "courses", type_="check"
    )
    op.drop_column("courses", "duration_hours")


def downgrade() -> None:
    op.add_column(
        "courses",
        sa.Column("duration_hours", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        UPDATE courses
        SET duration_hours = duration_value * CASE duration_unit
            WHEN 'hours' THEN 1
            WHEN 'days' THEN 24
            WHEN 'weeks' THEN 168
            WHEN 'months' THEN 720
            WHEN 'years' THEN 8760
        END
        """
    )
    op.alter_column(
        "courses",
        "duration_hours",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_check_constraint(
        "ck_course_duration_hours_positive",
        "courses",
        "duration_hours > 0",
    )
