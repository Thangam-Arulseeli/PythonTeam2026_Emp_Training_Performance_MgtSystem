from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course_content import CourseContent
from app.repositories.interfaces.course_content_interface import (
    CourseContentInterface,
)


class CourseContentRepository(CourseContentInterface):

    def __init__(self, db: AsyncSession):
        """Create the content repository for the supplied async database session."""
        self.db = db

    async def create(
        self, course_id: int, filename: str, file_path: str
    ) -> CourseContent:
        """Insert content metadata, commit it, and refresh its database fields."""
        content = CourseContent(
            course_id=course_id,
            filename=filename,
            file_path=file_path,
        )

        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)

        return content

    async def get_by_id(self, content_id: int) -> Optional[CourseContent]:
        """Return content metadata by primary key, or None when absent."""
        return await self.db.get(CourseContent, content_id)

    async def get_by_course(self, course_id: int) -> List[CourseContent]:
        """Return all content records associated with a course."""
        stmt = select(CourseContent).where(CourseContent.course_id == course_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, content: CourseContent) -> None:
        """Delete a content metadata record and commit the transaction."""
        await self.db.delete(content)
        await self.db.commit()
