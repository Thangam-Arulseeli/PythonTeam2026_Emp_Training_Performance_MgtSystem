from abc import ABC, abstractmethod

from app.schemas.courseSchema import (
    CourseCreate,
    CourseListResponse,
    CourseResponse,
    CourseUpdate,
)


class CourseService(ABC):
    @abstractmethod
    async def create_course(self, payload: CourseCreate) -> CourseResponse: ...

    @abstractmethod
    async def get_course(self, course_id: int) -> CourseResponse: ...

    @abstractmethod
    async def list_courses(
        self, page: int, size: int, search: str | None = None
    ) -> CourseListResponse: ...

    @abstractmethod
    async def update_course(
        self, course_id: int, payload: CourseUpdate
    ) -> CourseResponse: ...

    @abstractmethod
    async def delete_course(self, course_id: int) -> None: ...
