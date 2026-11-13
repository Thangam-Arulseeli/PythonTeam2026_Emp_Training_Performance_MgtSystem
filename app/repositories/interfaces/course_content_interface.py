from abc import ABC, abstractmethod

from app.models.course_content import CourseContent


class CourseContentInterface(ABC):

    @abstractmethod
    async def create(
        self, course_id: int, filename: str, file_path: str
    ) -> CourseContent:
        """Persist file metadata associated with a course."""
        pass

    @abstractmethod
    async def get_by_id(self, content_id: int) -> CourseContent | None:
        """Return content metadata by ID, or None when it does not exist."""
        pass

    @abstractmethod
    async def get_by_course(self, course_id: int) -> list[CourseContent]:
        """Return all content metadata associated with a course."""
        pass

    @abstractmethod
    async def delete(self, content: CourseContent) -> None:
        """Delete a persisted content metadata record."""
        pass
