from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trainer_resume import TrainerResume
from app.repositories.interfaces.trainer_resume_repository import (
    TrainerResumeRepository,
)


class TrainerResumeRepositoryImpl(TrainerResumeRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_resume_by_trainer_id(
        self,
        trainer_id: int,
    ) -> TrainerResume | None:
        result = await self.db.execute(
            select(TrainerResume).where(TrainerResume.trainer_id == trainer_id)
        )
        return result.scalar_one_or_none()

    async def create_trainer_resume(self, resume_data: dict) -> TrainerResume:
        resume = TrainerResume(**resume_data)
        self.db.add(resume)
        try:
            await self.db.commit()
            await self.db.refresh(resume)
        except Exception:
            await self.db.rollback()
            raise
        return resume
