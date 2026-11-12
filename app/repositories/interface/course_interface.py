from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.models.course import Course


class CourseInterface(ABC):
    @abstractmethod
    async def create(self, data: dict) -> Course:
        pass

    @abstractmethod
    async def get_by_id(self, course_id: int) -> Optional[Course]:
        pass

    @abstractmethod
    async def get_by_name(self, course_name: str) -> Optional[Course]:
        pass

    @abstractmethod
    async def get_all(
        self, skip: int, limit: int, search: Optional[str] = None
    ) -> Tuple[List[Course], int]:
        pass

    @abstractmethod
    async def update(self, course: Course, data: dict) -> Course:
        pass

    @abstractmethod
    async def delete(self, course: Course) -> None:
        pass

    @abstractmethod
    async def has_batches(self, course_id: int) -> bool:
        pass

    @abstractmethod
    async def get_content_file_paths(self, course_id: int) -> List[str]:
        pass
