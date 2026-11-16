from abc import ABC, abstractmethod

from app.models.course import Course


class CourseInterface(ABC):
    @abstractmethod
    async def create(self, data: dict) -> Course:
        """Persist a course from its field dictionary."""
        pass

    @abstractmethod
    async def get_by_id(self, course_id: int) -> Course | None:
        """Return a course by ID, or None when it does not exist."""
        pass

    @abstractmethod
    async def get_by_name(self, course_name: str) -> Course | None:
        """Find a course by name, or return None when it does not exist."""
        pass

    @abstractmethod
    async def get_all(
        self, skip: int, limit: int, search: str | None = None
    ) -> tuple[list[Course], int]:
        """Return a course page and total count, optionally filtered by search."""
        pass

    @abstractmethod
    async def update(self, course: Course, data: dict) -> Course:
        """Apply the supplied fields to a persisted course."""
        pass

    @abstractmethod
    async def delete(self, course: Course) -> None:
        """Delete a persisted course."""
        pass

    @abstractmethod
    async def has_batches(self, course_id: int) -> bool:
        """Check whether any batch is associated with a course."""
        pass

    @abstractmethod
    async def get_content_file_paths(self, course_id: int) -> list[str]:
        """Return filesystem paths for the course's uploaded content."""
        pass
