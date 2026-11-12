from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.course_content import CourseContent


class CourseContentInterface(ABC):

    @abstractmethod
    async def create(
        self, course_id: int, filename: str, file_path: str
    ) -> CourseContent:
        pass

    @abstractmethod
    async def get_by_id(self, content_id: int) -> Optional[CourseContent]:
        pass

    @abstractmethod
    async def get_by_course(self, course_id: int) -> List[CourseContent]:
        pass

    @abstractmethod
    async def delete(self, content: CourseContent) -> None:
        pass
