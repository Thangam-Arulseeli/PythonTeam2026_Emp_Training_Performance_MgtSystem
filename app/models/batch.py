from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.trainer import Trainer  # teammate's model


class Batch(Base):
    __tablename__ = "batches"
    __table_args__ = (
        CheckConstraint("end_date > start_date", name="ck_batch_dates"),
        CheckConstraint(
            "status IN ('completed', 'not_completed')", name="ck_batch_status"
        ),
        Index("ix_batches_course_id", "course_id"),
        Index("ix_batches_trainer_id", "trainer_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_name: Mapped[str] = mapped_column(String(100))
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="RESTRICT")
    )
    trainer_id: Mapped[int] = mapped_column(
        ForeignKey("trainers.trainer_id", ondelete="RESTRICT")
    )
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="not_completed",
        server_default="not_completed",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    course: Mapped["Course"] = relationship(back_populates="batches")
    trainer: Mapped["Trainer"] = relationship()
