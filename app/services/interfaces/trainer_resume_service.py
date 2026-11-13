from abc import ABC, abstractmethod

from fastapi import UploadFile

from app.schemas.trainer_resume import TrainerResumeResponse


class TrainerResumeService(ABC):
    @abstractmethod
    async def upload_trainer_resume(
        self,
        trainer_id: int,
        file: UploadFile,
    ) -> TrainerResumeResponse:
        pass
