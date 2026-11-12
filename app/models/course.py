from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.batch import Batch
    from app.models.course_content import CourseContent


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("duration > 0", name="ck_course_duration_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    course_name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    course_contents: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # topics text
    duration: Mapped[int] = mapped_column(Integer)  # in days

    batches: Mapped[List["Batch"]] = relationship(back_populates="course")
    contents: Mapped[List["CourseContent"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
