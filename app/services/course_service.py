import os
from typing import Optional

from app.exceptions import (
    ConflictException,
    NotFoundException,
    UnprocessableEntityException,
)
from app.repositories.interfaces.course_interface import CourseInterface
from app.schemas.courseSchema import (
    CourseCreate,
    CourseListResponse,
    CourseResponse,
    CourseUpdate,
)
from app.utils.logger import logger


class CourseService:
    def __init__(self, course_repo: CourseInterface):
        """Create the course service with its persistence interface."""
        self.course_repo = course_repo

    async def _get_or_404(self, course_id: int):
        """Load a course by ID or raise a not-found error."""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            logger.warning("Course not found: course_id=%s", course_id)
            raise NotFoundException("Course not found")
        return course

    async def create_course(self, payload: CourseCreate) -> CourseResponse:
        """Reject duplicate names, persist a course, and return its response model."""
        existing = await self.course_repo.get_by_name(payload.course_name)
        if existing:
            logger.warning("Course creation conflict: name '%s' already exists", payload.course_name)
            raise ConflictException("Course name already exists")
        created = await self.course_repo.create(payload.model_dump())
        logger.info("Course created successfully: id=%s, name='%s'", created.id, created.course_name)
        return CourseResponse.model_validate(created)

    async def get_course(self, course_id: int) -> CourseResponse:
        """Return the requested course or raise a not-found error."""
        course = await self._get_or_404(course_id)
        return CourseResponse.model_validate(course)

    async def list_courses(
        self, page: int, size: int, search: Optional[str] = None
    ) -> CourseListResponse:
        """Fetch a page of courses and include the total matching result count."""
        skip = max(0, (page - 1) * size)
        items, total = await self.course_repo.get_all(skip, size, search)
        return CourseListResponse(
            items=[CourseResponse.model_validate(c) for c in items],
            total=total,
            page=page,
            size=size,
        )

    async def update_course(
        self, course_id: int, payload: CourseUpdate
    ) -> CourseResponse:
        """Validate update fields and name uniqueness, then persist the changes."""
        course = await self._get_or_404(course_id)
        data = payload.model_dump(exclude_unset=True)
        if "course_name" in data and data["course_name"] is None:
            raise UnprocessableEntityException("course_name cannot be null")
        if "duration" in data and data["duration"] is None:
            raise UnprocessableEntityException("duration cannot be null")
        new_name = data.get("course_name")
        if new_name:
            existing = await self.course_repo.get_by_name(new_name)
            if existing and existing.id != course_id:
                logger.warning("Course update conflict: name '%s' already exists for another course", new_name)
                raise ConflictException("Course name already exists")
        updated = await self.course_repo.update(course, data)
        logger.info("Course updated successfully: id=%s", course_id)
        return CourseResponse.model_validate(updated)

    async def delete_course(self, course_id: int) -> None:
        """Delete a course without batches and remove its associated content files."""
        course = await self._get_or_404(course_id)
        if await self.course_repo.has_batches(course_id):
            logger.warning("Cannot delete course: id=%s has associated batches", course_id)
            raise ConflictException("Cannot delete a course that has batches")
        file_paths = await self.course_repo.get_content_file_paths(course_id)
        await self.course_repo.delete(course)
        logger.info("Course deleted from database: id=%s", course_id)
        for path in file_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info("Deleted associated content file: %s", path)
                except OSError as exc:
                    logger.error("Failed to delete content file %s: %s", path, exc)
