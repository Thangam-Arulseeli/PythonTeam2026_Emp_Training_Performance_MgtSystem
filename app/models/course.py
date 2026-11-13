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
        CheckConstraint(
            "duration_value > 0", name="ck_course_duration_value_positive"
        ),
        CheckConstraint(
            "duration_unit IN ('hours', 'days', 'weeks', 'months', 'years')",
            name="ck_course_duration_unit",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    course_name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    course_contents: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text()), nullable=True
    )
    duration_value: Mapped[int] = mapped_column(Integer)
    duration_unit: Mapped[str] = mapped_column(String(10))

    batches: Mapped[list["Batch"]] = relationship(back_populates="course")
    contents: Mapped[list["CourseContent"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
