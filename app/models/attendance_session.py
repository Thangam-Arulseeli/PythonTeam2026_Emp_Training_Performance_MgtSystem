from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import AttendanceSessionStatus
from app.database import Base

if TYPE_CHECKING:
    from app.models.attendance_record import AttendanceRecord
    from app.models.batch import Batch


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    __table_args__ = (
        CheckConstraint(
            "end_time > start_time",
            name="ck_attendance_session_time",
        ),
        Index("ix_attendance_sessions_batch_date", "batch_id", "session_date"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    batch_id: Mapped[int] = mapped_column(
        ForeignKey("batches.id", ondelete="RESTRICT"),
        nullable=False,
    )

    session_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[AttendanceSessionStatus] = mapped_column(
        Enum(
            AttendanceSessionStatus,
            name="attendance_session_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=AttendanceSessionStatus.SCHEDULED,
        server_default="scheduled",
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

    batch: Mapped["Batch"] = relationship()

    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        "AttendanceRecord",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    