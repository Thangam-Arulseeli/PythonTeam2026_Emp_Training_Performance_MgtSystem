"""Store course topics as a PostgreSQL string array.

Revision ID: 41c82af036d1
Revises: 2c03ef86aa14
Create Date: 2026-11-12
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "41c82af036d1"
down_revision: Union[str, None] = "2c03ef86aa14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "courses",
        "course_contents",
        existing_type=postgresql.TEXT(),
        type_=postgresql.ARRAY(postgresql.TEXT()),
        existing_nullable=True,
        postgresql_using="string_to_array(course_contents, ',')",
    )


def downgrade() -> None:
    op.alter_column(
        "courses",
        "course_contents",
        existing_type=postgresql.ARRAY(postgresql.TEXT()),
        type_=postgresql.TEXT(),
        existing_nullable=True,
        postgresql_using="array_to_string(course_contents, ',')",
    )
