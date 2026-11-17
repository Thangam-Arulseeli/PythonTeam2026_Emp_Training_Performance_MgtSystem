from decimal import Decimal
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func

from app.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("assessments.id"), nullable=False, index=True
    )
    enrollment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enrollments.enrollment_id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="pending")
    mark: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    submitted_date_time: Mapped[datetime | None] = mapped_column(DateTime)
    evaluated_date_time: Mapped[datetime | None] = mapped_column(DateTime)
    feedback: Mapped[str | None] = mapped_column(String(300))
    grade: Mapped[str | None] = mapped_column(String(10), index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
