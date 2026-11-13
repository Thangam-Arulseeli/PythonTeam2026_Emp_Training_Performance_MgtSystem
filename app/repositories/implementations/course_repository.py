
from sqlalchemy import exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch import Batch
from app.models.course import Course
from app.models.course_content import CourseContent
from app.repositories.interfaces.course_interface import CourseInterface


class CourseRepository(CourseInterface):

    def __init__(self, db: AsyncSession):
        """Create the course repository for the supplied async database session."""
        self.db = db

    async def create(self, data: dict) -> Course:
        """Insert a course, commit the transaction, and refresh its database fields."""
        course = Course(**data)
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def get_by_id(self, course_id: int) -> Course | None:
        """Return a course by primary key, or None when it does not exist."""
        return await self.db.get(Course, course_id)

    async def get_by_name(self, course_name: str) -> Course | None:
        """Find a course by name without regard to case or surrounding spaces."""
        stmt = select(Course).where(
            func.lower(Course.course_name) == course_name.strip().lower()
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int, limit: int, search: str | None = None
    ) -> tuple[list[Course], int]:
        """Return an ordered course page and the total count matching the search."""
        stmt = select(Course)

        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Course.course_name.ilike(pattern),
                    Course.description.ilike(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar_one() or 0

        courses_stmt = stmt.order_by(Course.id).offset(skip).limit(limit)
        courses_res = await self.db.execute(courses_stmt)
        courses = courses_res.scalars().all()

        return list(courses), total

    async def update(self, course: Course, data: dict) -> Course:
        """Apply supplied fields to a course, commit, and refresh it."""
        for key, value in data.items():
            setattr(course, key, value)

        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def delete(self, course: Course) -> None:
        """Delete a course and commit the transaction."""
        await self.db.delete(course)
        await self.db.commit()

    async def has_batches(self, course_id: int) -> bool:
        """Return whether any batch references the given course."""
        stmt = select(exists().where(Batch.course_id == course_id))
        result = await self.db.execute(stmt)
        return bool(result.scalar())

    async def get_content_file_paths(self, course_id: int) -> list[str]:
        """Return stored file paths for uploaded content belonging to a course."""
        stmt = select(CourseContent.file_path).where(
            CourseContent.course_id == course_id
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
