import os
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException, UploadFile, status

from app.repositories.interface.course_content_interface import (
    CourseContentInterface,
)
from app.repositories.interface.course_interface import CourseInterface
from app.schema.course_content_schema import (
    CourseContentListResponse,
    CourseContentResponse,
)

UPLOAD_DIR = Path("uploads/course_content")
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}
MAX_FILE_SIZE = 50 * 1024 * 1024


class CourseContentService:

    def __init__(
        self,
        content_repo: CourseContentInterface,
        course_repo: CourseInterface,
    ):
        self.content_repo = content_repo
        self.course_repo = course_repo

    async def get_content_or_404(self, content_id: int):
        content = await self.content_repo.get_by_id(content_id)

        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course content not found",
            )

        return content

    async def upload(self, course_id: int, file: UploadFile) -> CourseContentResponse:

        if not await self.course_repo.get_by_id(course_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        filename = os.path.basename(file.filename or "")
        extension = Path(filename).suffix.lower()

        if not filename or extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
            )

        course_dir = UPLOAD_DIR / str(course_id)
        course_dir.mkdir(parents=True, exist_ok=True)

        file_path = course_dir / f"{uuid.uuid4().hex}_{filename}"
        size = 0

        try:
            with open(file_path, "wb") as output:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)

                    if size > MAX_FILE_SIZE:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="File too large. Maximum size is 50 MB",
                        )

                    output.write(chunk)

            content = await self.content_repo.create(
                course_id=course_id,
                filename=filename,
                file_path=str(file_path),
            )

            return CourseContentResponse.model_validate(content)

        except Exception:
            if file_path.exists():
                file_path.unlink()
            raise

    async def list_for_course(self, course_id: int) -> CourseContentListResponse:

        if not await self.course_repo.get_by_id(course_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        items = await self.content_repo.get_by_course(course_id)

        return CourseContentListResponse(
            items=[CourseContentResponse.model_validate(item) for item in items],
            total=len(items),
            page=1,
            size=max(len(items), 1),
        )

    async def get_file(self, content_id: int) -> Tuple[str, str]:

        content = await self.get_content_or_404(content_id)
        file_path = content.file_path

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on server",
            )

        return file_path, content.filename

    async def delete(self, content_id: int) -> None:

        content = await self.get_content_or_404(content_id)
        file_path = content.file_path

        await self.content_repo.delete(content)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
