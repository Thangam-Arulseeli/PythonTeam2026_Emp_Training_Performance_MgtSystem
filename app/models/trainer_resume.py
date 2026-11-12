from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.trainer import Trainer


class TrainerResume(Base):
    __tablename__ = "trainer_resumes"

    resume_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    trainer_id: Mapped[int] = mapped_column(
        ForeignKey("trainers.trainer_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    trainer: Mapped["Trainer"] = relationship(
        back_populates="resume",
    )
