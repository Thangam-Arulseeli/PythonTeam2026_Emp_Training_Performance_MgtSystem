from abc import ABC, abstractmethod

from fastapi import UploadFile

from app.schemas.course_content_schema import (
    CourseContentListResponse,
    CourseContentResponse,
)


class CourseContentService(ABC):
    @abstractmethod
    async def upload(self, course_id: int, file: UploadFile) -> CourseContentResponse: ...

    @abstractmethod
    async def list_for_course(self, course_id: int) -> CourseContentListResponse: ...

    @abstractmethod
    async def get_file(self, content_id: int) -> tuple[str, str]: ...

    @abstractmethod
    async def delete(self, content_id: int) -> None: ...
