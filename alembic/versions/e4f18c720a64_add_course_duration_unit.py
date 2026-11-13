"""Store entered course duration and its unit alongside normalized hours.

Revision ID: e4f18c720a64
Revises: d2c6b716a8e1
Create Date: 2026-11-13
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e4f18c720a64"
down_revision: str | None = "d2c6b716a8e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("duration_value", sa.Integer(), nullable=True))
    op.add_column(
        "courses", sa.Column("duration_unit", sa.String(length=10), nullable=True)
    )
    op.execute(
        "UPDATE courses "
        "SET duration_value = duration_hours, duration_unit = 'hours'"
    )
    op.alter_column(
        "courses",
        "duration_value",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "courses",
        "duration_unit",
        existing_type=sa.String(length=10),
        nullable=False,
    )
    op.create_check_constraint(
        "ck_course_duration_value_positive", "courses", "duration_value > 0"
    )
    op.create_check_constraint(
        "ck_course_duration_unit",
        "courses",
        "duration_unit IN ('hours', 'days', 'weeks', 'months', 'years')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_course_duration_unit", "courses", type_="check")
    op.drop_constraint(
        "ck_course_duration_value_positive", "courses", type_="check"
    )
    op.drop_column("courses", "duration_unit")
    op.drop_column("courses", "duration_value")
