from typing import List, Optional, Tuple

from sqlalchemy import exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch import Batch
from app.models.course import Course
from app.models.course_content import CourseContent
from app.repositories.interface.course_interface import CourseInterface


class CourseRepository(CourseInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Course:
        course = Course(**data)
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def get_by_id(self, course_id: int) -> Optional[Course]:
        return await self.db.get(Course, course_id)

    async def get_by_name(self, course_name: str) -> Optional[Course]:
        stmt = select(Course).where(
            func.lower(Course.course_name) == course_name.strip().lower()
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int, limit: int, search: Optional[str] = None
    ) -> Tuple[List[Course], int]:
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
        for key, value in data.items():
            setattr(course, key, value)

        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def delete(self, course: Course) -> None:
        await self.db.delete(course)
        await self.db.commit()

    async def has_batches(self, course_id: int) -> bool:
        stmt = select(exists().where(Batch.course_id == course_id))
        result = await self.db.execute(stmt)
        return bool(result.scalar())

    async def get_content_file_paths(self, course_id: int) -> List[str]:
        stmt = select(CourseContent.file_path).where(CourseContent.course_id == course_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
