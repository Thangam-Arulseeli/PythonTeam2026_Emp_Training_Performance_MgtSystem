from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.assessment import Assessment
    from app.models.enrollment import Enrollment


class AssessmentResultStatus(StrEnum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    GRADED = "graded"
    CANCELLED = "cancelled"


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "enrollment_id",
            name="uq_assessment_results_assessment_enrollment",
        ),
        CheckConstraint(
            f"status IN {tuple(s.value for s in AssessmentResultStatus)}",
            name="ck_assessment_results_status",
        ),
        CheckConstraint(
            "mark IS NULL OR mark >= 0",
            name="ck_assessment_results_mark_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enrollment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("enrollments.enrollment_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=AssessmentResultStatus.PENDING,
        server_default="pending",
        index=True,
    )

    mark: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    grade: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )
    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    file_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    submitted_date_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    evaluated_date_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
    )
    enrollment: Mapped["Enrollment"] = relationship(
        "Enrollment",
    )
