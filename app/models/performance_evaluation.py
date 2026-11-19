from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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
    from app.models.enrollment import Enrollment
    from app.models.user import User


class PerformanceEvaluationStatus(StrEnum):
    DRAFT = "draft"
    COMPLETED = "completed"


class PerformanceEvaluation(Base):
    __tablename__ = "performance_evaluations"

    __table_args__ = (
        UniqueConstraint(
            "enrollment_id",
            name="uq_performance_evaluations_enrollment",
        ),
        CheckConstraint(
            f"status IN {tuple(s.value for s in PerformanceEvaluationStatus)}",
            name="ck_performance_evaluations_status",
        ),
        CheckConstraint(
            "assessment_score_pct >= 0 AND assessment_score_pct <= 100",
            name="ck_performance_evaluations_assessment_score_pct",
        ),
        CheckConstraint(
            "attendance_pct >= 0 AND attendance_pct <= 100",
            name="ck_performance_evaluations_attendance_pct",
        ),
        CheckConstraint(
            "communication_score >= 0 AND communication_score <= 100",
            name="ck_performance_evaluations_communication_score",
        ),
        CheckConstraint(
            "behaviour_score >= 0 AND behaviour_score <= 100",
            name="ck_performance_evaluations_behaviour_score",
        ),
        CheckConstraint(
            "teamwork_score >= 0 AND teamwork_score <= 100",
            name="ck_performance_evaluations_teamwork_score",
        ),
        CheckConstraint(
            "final_score >= 0 AND final_score <= 100",
            name="ck_performance_evaluations_final_score",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enrollment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("enrollments.enrollment_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    evaluator_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    assessment_score_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    attendance_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    communication_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    behaviour_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    teamwork_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    final_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    grade: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Needs Improvement",
    )
    is_certified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=PerformanceEvaluationStatus.DRAFT.value,
    )
    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    evaluated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    enrollment: Mapped["Enrollment"] = relationship("Enrollment")
    evaluator: Mapped["User"] = relationship("User")
