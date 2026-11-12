from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trainer import Trainer
from app.repositories.interfaces.trainer_repository import TrainerRepository


class TrainerRepositoryImpl(TrainerRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_trainer(self, trainer_data: dict) -> Trainer:

        trainer = Trainer(**trainer_data)

        self.db.add(trainer)
        await self.db.commit()
        await self.db.refresh(trainer)

        return trainer

    async def get_all_trainers(self) -> list[Trainer]:

        result = await self.db.execute(select(Trainer))

        return list(result.scalars().all())

    async def get_trainer_by_id(self, trainer_id: int) -> Trainer | None:

        result = await self.db.execute(
            select(Trainer).where(Trainer.trainer_id == trainer_id)
        )

        return result.scalar_one_or_none()

    async def update_trainer(
        self,
        trainer_id: int,
        trainer_data: dict,
    ) -> Trainer | None:

        trainer = await self.get_trainer_by_id(trainer_id)

        if trainer is None:
            return None

        for key, value in trainer_data.items():
            setattr(trainer, key, value)

        await self.db.commit()
        await self.db.refresh(trainer)

        return trainer

    async def update_trainer_status(
        self,
        trainer_id: int,
        is_active: bool,
    ) -> Trainer | None:

        trainer = await self.get_trainer_by_id(trainer_id)

        if trainer is None:
            return None

        trainer.is_active = is_active

        await self.db.commit()
        await self.db.refresh(trainer)

        return trainer