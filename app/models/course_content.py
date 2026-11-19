from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.course import Course


class CourseContent(Base):
    __tablename__ = "course_contents"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))  # original file name
    file_path: Mapped[str] = mapped_column(String(500))  # stored file path

    course: Mapped["Course"] = relationship(back_populates="contents")
