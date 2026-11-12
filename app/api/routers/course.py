from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependency.deps import get_course_service
from app.schema.courseSchema import (
    CourseCreate,
    CourseListResponse,
    CourseResponse,
    CourseUpdate,
)
from app.services.course_service import CourseService

router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
)


@router.post(
    "/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new course",
)
async def create_course(
    payload: CourseCreate,
    service: CourseService = Depends(get_course_service),
):
    return await service.create_course(payload)


@router.get(
    "/",
    response_model=CourseListResponse,
    summary="Get paginated list of courses",
)
async def list_courses(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(
        None, description="Search term for course name or description"
    ),
    service: CourseService = Depends(get_course_service),
):
    return await service.list_courses(page=page, size=size, search=search)


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Get a course by ID",
)
async def get_course(
    course_id: int,
    service: CourseService = Depends(get_course_service),
):
    return await service.get_course(course_id)


@router.put(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Update a course",
)
async def update_course(
    course_id: int,
    payload: CourseUpdate,
    service: CourseService = Depends(get_course_service),
):
    return await service.update_course(course_id, payload)


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a course",
)
async def delete_course(
    course_id: int,
    service: CourseService = Depends(get_course_service),
):
    await service.delete_course(course_id)
