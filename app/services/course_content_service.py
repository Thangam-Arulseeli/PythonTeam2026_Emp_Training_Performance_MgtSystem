import os
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile

from app.exceptions import (
    BadRequestException,
    NotFoundException,
    PayloadTooLargeException,
)
from app.repositories.interface.course_content_interface import (
    CourseContentInterface,
)
from app.repositories.interface.course_interface import CourseInterface
from app.schemas.course_content_schema import (
    CourseContentListResponse,
    CourseContentResponse,
)
from app.utils.logger import logger

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
            logger.warning("Course content not found: content_id=%s", content_id)
            raise NotFoundException("Course content not found")

        return content

    async def upload(self, course_id: int, file: UploadFile) -> CourseContentResponse:

        if not await self.course_repo.get_by_id(course_id):
            logger.warning("Upload failed: Course not found course_id=%s", course_id)
            raise NotFoundException("Course not found")

        filename = os.path.basename(file.filename or "")
        extension = Path(filename).suffix.lower()

        if not filename or extension not in ALLOWED_EXTENSIONS:
            logger.warning("Upload rejected: unsupported file extension '%s'", extension)
            raise BadRequestException(
                f"Unsupported file type. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
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
                        logger.warning("Upload rejected: file size %s exceeds %s", size, MAX_FILE_SIZE)
                        raise PayloadTooLargeException(
                            "File too large. Maximum size is 50 MB"
                        )

                    output.write(chunk)

            content = await self.content_repo.create(
                course_id=course_id,
                filename=filename,
                file_path=str(file_path),
            )

            logger.info("Course content uploaded successfully: id=%s for course=%s", content.id, course_id)
            return CourseContentResponse.model_validate(content)

        except Exception as exc:
            if file_path.exists():
                file_path.unlink()
            if not isinstance(exc, (BadRequestException, NotFoundException, PayloadTooLargeException)):
                logger.exception("Error uploading course content file: %s", exc)
            raise

    async def list_for_course(self, course_id: int) -> CourseContentListResponse:

        if not await self.course_repo.get_by_id(course_id):
            logger.warning("list_for_course failed: Course not found id=%s", course_id)
            raise NotFoundException("Course not found")

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
            logger.error("Content file missing on disk: path=%s for content_id=%s", file_path, content_id)
            raise NotFoundException("File not found on server")

        logger.info("Serving content file download: content_id=%s, filename='%s'", content_id, content.filename)
        return file_path, content.filename

    async def delete(self, content_id: int) -> None:

        content = await self.get_content_or_404(content_id)
        file_path = content.file_path

        await self.content_repo.delete(content)
        logger.info("Content record deleted from database: content_id=%s", content_id)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info("Content file deleted from disk: %s", file_path)
            except OSError as exc:
                logger.error("Failed to delete content file from disk %s: %s", file_path, exc)
