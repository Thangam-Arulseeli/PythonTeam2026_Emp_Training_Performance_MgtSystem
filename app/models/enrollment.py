from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.batch import Batch
    from app.models.employee import EmployeeData


class Enrollment(Base):
    __tablename__ = "enrollments"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "batch_id",
            name="uq_enrollment_employee_batch",
        ),
        CheckConstraint(
            "status IN ('enrolled', 'cancelled', 'paused', 'completed')",
            name="ck_enrollment_status",
        ),
    )

    enrollment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("employee.employee_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    batch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("batches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    enrollment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(15), default="enrolled", server_default="enrolled", nullable=False
    )
    status_update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    employee: Mapped["EmployeeData"] = relationship(
        "EmployeeData", back_populates="enrollments"
    )
    batch: Mapped["Batch"] = relationship("Batch", back_populates="enrollments")
