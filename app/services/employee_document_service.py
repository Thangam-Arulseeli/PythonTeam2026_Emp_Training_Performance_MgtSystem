
import asyncio
import io
import zipfile

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee_document import EmployeeDocument

from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface,
)

from app.repositories.interfaces.employee_document_interface import (
    EmployeeDocumentRepositoryInterface,
)

from app.exceptions.exceptions import (
    EmployeeNotFoundException,
    InvalidEmployeeDataException,
    EmployeeAlreadyExistsException,
)


UPLOAD_DIR = Path("uploads")

IMAGE_MAX_SIZE = 2 * 1024 * 1024
RESUME_MAX_SIZE = 5 * 1024 * 1024


class EmployeeDocumentService:

    def __init__(
        self,
        db: AsyncSession,
        employee_repository: EmployeeRepositoryInterface,
        document_repository: EmployeeDocumentRepositoryInterface,
    ):
        self.db = db
        self.employee_repository = employee_repository
        self.document_repository = document_repository

    # CHECK EMPLOYEE
    async def check_employee(
        self,
        employee_id: int,
    ) -> None:

        employee = (
            await self.employee_repository.get_employee_by_id(
                employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundException()

    # VALIDATE AND STORE FILE
    async def save_file(
        self,
        file: UploadFile,
        document_type: str,
    ) -> str:

        if document_type == "profile_picture":
            allowed_extensions = {".jpg", ".jpeg", ".png"}
            max_size = IMAGE_MAX_SIZE
            folder = "profiles"
        else:
            allowed_extensions = {".pdf", ".docx"}
            max_size = RESUME_MAX_SIZE
            folder = "resumes"

        extension = Path(
            file.filename or ""
        ).suffix.lower()

        if extension not in allowed_extensions:
            raise InvalidEmployeeDataException(
                f"Invalid file format for {document_type}"
            )

        content = await file.read(max_size + 1)

        if not content:
            raise InvalidEmployeeDataException(
                "Uploaded file cannot be empty"
            )

        if len(content) > max_size:
            raise InvalidEmployeeDataException(
                f"{document_type} exceeds allowed file size"
            )

        # Validate the file signature.
        if extension in {".jpg", ".jpeg"}:
            valid = content.startswith(b"\xff\xd8\xff")

        elif extension == ".png":
            valid = content.startswith(
                b"\x89PNG\r\n\x1a\n"
            )

        elif extension == ".pdf":
            valid = content.startswith(b"%PDF-")

        else:
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as archive:
                    valid = (
                        "word/document.xml" in archive.namelist()
                        and "[Content_Types].xml" in archive.namelist()
                    )
            except (zipfile.BadZipFile, OSError, ValueError):
                valid = False

        if not valid:
            raise InvalidEmployeeDataException(
                f"File content does not match {extension}"
            )

        directory = UPLOAD_DIR / folder

        await asyncio.to_thread(
            directory.mkdir,
            parents=True,
            exist_ok=True
        )

        filename = f"{uuid4().hex}{extension}"
        file_path = directory / filename

        await asyncio.to_thread(
            file_path.write_bytes,
            content
        )

        return str(file_path)

    # UPLOAD PROFILE PICTURE AND RESUME
    async def upload_documents(
        self,
        employee_id: int,
        profile_picture: UploadFile,
        resume: UploadFile,
    ) -> list[EmployeeDocument]:

        await self.check_employee(employee_id)

        existing_documents = (
            await self.document_repository
            .get_documents_by_employee_id(employee_id)
        )

        if existing_documents:
            raise EmployeeAlreadyExistsException(
                "documents"
            )

        saved_paths = []

        try:
            profile_path = await self.save_file(
                profile_picture,
                "profile_picture"
            )
            saved_paths.append(profile_path)

            resume_path = await self.save_file(
                resume,
                "resume"
            )
            saved_paths.append(resume_path)

            documents = [
                EmployeeDocument(
                    employee_id=employee_id,
                    document_type="profile_picture",
                    file_path=profile_path,
                ),
                EmployeeDocument(
                    employee_id=employee_id,
                    document_type="resume",
                    file_path=resume_path,
                ),
            ]

            documents = (
                await self.document_repository.create_documents(
                    documents
                )
            )

            await self.db.commit()

            for document in documents:
                await self.db.refresh(document)

            return documents

        except Exception as exc:
            await self.db.rollback()

            # Remove newly saved files on failure.
            for path in saved_paths:
                await asyncio.to_thread(
                    Path(path).unlink,
                    missing_ok=True
                )

            if (
                isinstance(exc, IntegrityError)
                and getattr(exc.orig, "sqlstate", None)
                == "23505"
            ):
                raise EmployeeAlreadyExistsException(
                    "documents"
                ) from exc

            raise

    # GET EMPLOYEE DOCUMENTS
    async def get_documents(
        self,
        employee_id: int,
    ) -> list[EmployeeDocument]:

        await self.check_employee(employee_id)

        return (
            await self.document_repository
            .get_documents_by_employee_id(employee_id)
        )
