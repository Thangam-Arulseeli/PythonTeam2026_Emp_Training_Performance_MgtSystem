from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.repositories.interfaces.trainer_repository import TrainerRepository
from app.repositories.interfaces.trainer_resume_repository import (
    TrainerResumeRepository,
)
from app.schemas.trainer_resume import TrainerResumeResponse
from app.services.interfaces.trainer_resume_service import TrainerResumeService


class TrainerResumeServiceImpl(TrainerResumeService):
    def __init__(
        self,
        trainer_repository: TrainerRepository,
        resume_repository: TrainerResumeRepository,
    ):
        self.trainer_repository = trainer_repository
        self.resume_repository = resume_repository

    async def upload_trainer_resume(
        self,
        trainer_id: int,
        file: UploadFile,
    ) -> TrainerResumeResponse:
        file_path = None
        try:
            trainer = await self.trainer_repository.get_trainer_by_id(trainer_id)
            if trainer is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Trainer not found",
                )

            existing_resume = await self.resume_repository.get_resume_by_trainer_id(
                trainer_id
            )
            if existing_resume:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Resume already exists",
                )

            if not file.filename or not file.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only PDF files are allowed",
                )

            upload_dir = Path("uploads/trainer_resumes")
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / f"{uuid4().hex}.pdf"

            try:
                with file_path.open("xb") as buffer:
                    buffer.write(await file.read())

                resume_data = {
                    "trainer_id": trainer_id,
                    "file_name": file.filename,
                    "file_path": str(file_path),
                }
                return await self.resume_repository.create_trainer_resume(resume_data)
            except Exception as exc:
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to upload resume",
                ) from exc
        finally:
            await file.close()
