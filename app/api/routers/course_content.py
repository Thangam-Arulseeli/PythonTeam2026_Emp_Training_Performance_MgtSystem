from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependency.deps import get_course_content_service
from app.schema.course_content_schema import (
    CourseContentListResponse,
    CourseContentResponse,
)
from app.services.course_content_service import CourseContentService

router = APIRouter(
    prefix="/courses",
    tags=["Course Contents"],
)


@router.post(
    "/{course_id}/contents",
    response_model=CourseContentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload content file for a course",
)
async def upload_course_content(
    course_id: int,
    file: UploadFile = File(..., description="PDF, DOC, DOCX, or TXT file"),
    service: CourseContentService = Depends(get_course_content_service),
):
    return await service.upload(course_id=course_id, file=file)


@router.get(
    "/{course_id}/contents",
    response_model=CourseContentListResponse,
    summary="List all contents/files for a course",
)
async def list_course_contents(
    course_id: int,
    service: CourseContentService = Depends(get_course_content_service),
):
    return await service.list_for_course(course_id=course_id)


@router.get(
    "/contents/{content_id}/download",
    summary="Download a course content file",
)
async def download_course_content(
    content_id: int,
    service: CourseContentService = Depends(get_course_content_service),
):
    file_path, filename = await service.get_file(content_id=content_id)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.delete(
    "/contents/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a course content file",
)
async def delete_course_content(
    content_id: int,
    service: CourseContentService = Depends(get_course_content_service),
):
    await service.delete(content_id=content_id)
