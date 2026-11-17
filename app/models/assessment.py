from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)

from app.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

ASSESSMENT_TYPE = ("quiz", "interview", "exam")


class Assessment(Base):

    __tablename__ = "assessments"

    __table_args__ = (
        CheckConstraint(
            f"assessment_type IN {ASSESSMENT_TYPE}",
            name="ck_assessments_assessment_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("batches.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(300))
    assessment_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    scheduled_date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    total_mark: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    pass_mark: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
