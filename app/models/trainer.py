from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    String,
    Text,
    func,
    ARRAY
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.trainer_resume import TrainerResume


class Trainer(Base):
    __tablename__ = "trainers"

    __table_args__ = (
        CheckConstraint(
            "experience >= 0",
            name="ck_trainers_experience_non_negative",
        ),
        CheckConstraint(
            "dob <= CURRENT_DATE",
            name="ck_trainers_dob_not_future",
        ),
    )

    trainer_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    trainer_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    dob: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    experience: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    joining_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    specialization: Mapped[list[str]] = mapped_column(
        ARRAY(String(10)),
        nullable=False,
    )

    qualification: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    phone_number: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        nullable=False,
    )

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    resume: Mapped["TrainerResume"] = relationship(
        back_populates="trainer",
        cascade="all, delete-orphan",
        uselist=False,
    )
