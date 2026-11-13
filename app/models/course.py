from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, CheckConstraint, Integer, String, Text
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
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    course_contents: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text()), nullable=True
    )
    duration: Mapped[int] = mapped_column(Integer)  # in days

    batches: Mapped[list["Batch"]] = relationship(back_populates="course")
    contents: Mapped[list["CourseContent"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
