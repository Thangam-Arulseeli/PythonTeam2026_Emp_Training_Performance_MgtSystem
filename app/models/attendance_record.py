from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import AttendanceStatus
from app.database import Base

if TYPE_CHECKING:
    from app.models.attendance_session import AttendanceSession
    from app.models.enrollment import Enrollment
    from app.models.user import User


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "enrollment_id",
            name="uq_session_enrollment",
        ),
        Index("ix_attendance_records_enrollment", "enrollment_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollments.enrollment_id", ondelete="RESTRICT"),
        nullable=False,
    )

    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(
            AttendanceStatus,
            name="attendance_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    marked_by: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )

    marked_at: Mapped[datetime] = mapped_column(
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

    session: Mapped["AttendanceSession"] = relationship(
        "AttendanceSession",
        back_populates="attendance_records",
    )

    enrollment: Mapped["Enrollment"] = relationship(
        "Enrollment",
    )

    marked_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[marked_by],
    )
