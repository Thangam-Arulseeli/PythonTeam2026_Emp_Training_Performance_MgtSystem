from abc import ABC, abstractmethod

from app.models.trainer_resume import TrainerResume


class TrainerResumeRepository(ABC):
    @abstractmethod
    async def get_resume_by_trainer_id(
        self,
        trainer_id: int,
    ) -> TrainerResume | None:
        pass

    @abstractmethod
    async def create_trainer_resume(self, resume_data: dict) -> TrainerResume:
        pass
