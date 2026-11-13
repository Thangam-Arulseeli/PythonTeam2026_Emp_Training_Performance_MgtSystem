"""Store course duration in hours.

Revision ID: c1d09e4a7b32
Revises: be856e662948
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1d09e4a7b32"
down_revision: Union[str, None] = "be856e662948"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_course_duration_positive", "courses", type_="check")
    op.alter_column(
        "courses",
        "duration",
        new_column_name="duration_hours",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    op.execute("UPDATE courses SET duration_hours = duration_hours * 24")
    op.create_check_constraint(
        "ck_course_duration_hours_positive",
        "courses",
        "duration_hours > 0",
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM courses WHERE duration_hours % 24 <> 0
            ) THEN
                RAISE EXCEPTION
                    'Cannot downgrade: some course durations are not whole days';
            END IF;
        END $$;
        """
    )
    op.drop_constraint(
        "ck_course_duration_hours_positive", "courses", type_="check"
    )
    op.alter_column(
        "courses",
        "duration_hours",
        new_column_name="duration",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    op.execute("UPDATE courses SET duration = duration / 24")
    op.create_check_constraint(
        "ck_course_duration_positive",
        "courses",
        "duration > 0",
    )
