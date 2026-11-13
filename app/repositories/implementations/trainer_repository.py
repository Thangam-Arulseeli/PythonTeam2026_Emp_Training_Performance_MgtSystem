from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.trainer import Trainer
from app.models.trainer_resume import TrainerResume
from app.models.user import User
from app.repositories.interfaces.trainer_repository import TrainerRepository


class TrainerRepositoryImpl(TrainerRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_trainer(self, trainer_data: dict) -> Trainer:

        trainer = Trainer(**trainer_data)

        self.db.add(trainer)
        await self.db.commit()

        result = await self.db.execute(
            select(Trainer)
            .options(selectinload(Trainer.resume))
            .where(Trainer.trainer_id == trainer.trainer_id)
        )

        trainer = result.scalar_one()

        return trainer

    async def get_all_trainers(
        self,
        offset: int,
        limit: int,
        specialization: str | None = None,
        min_experience: int | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> list[Trainer]:

        query = select(Trainer).options(selectinload(Trainer.resume))

        if specialization is not None:
            query = query.where(Trainer.specialization.any(specialization))

        if min_experience is not None:
            query = query.where(Trainer.experience >= min_experience)

        if is_active is not None:
            query = query.where(Trainer.is_active == is_active)

        if search is not None:
            query = query.where(Trainer.trainer_name.ilike(f"%{search}%"))

        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)

        trainers = list(result.scalars().all())

        return trainers

    async def get_trainer_by_id(self, trainer_id: int) -> Trainer | None:

        result = await self.db.execute(
            select(Trainer)
            .options(selectinload(Trainer.resume))
            .where(Trainer.trainer_id == trainer_id)
        )

        trainer = result.scalar_one_or_none()

        return trainer

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

        result = await self.db.execute(
            select(Trainer)
            .options(selectinload(Trainer.resume))
            .where(Trainer.trainer_id == trainer_id)
        )

        trainer = result.scalar_one_or_none()

        return trainer

    async def update_trainer_status(
        self,
        trainer_id: int,
        is_active: bool,
    ) -> Trainer | None:

        trainer = await self.get_trainer_by_id(trainer_id)

        if trainer is None:
            return None
        try:

            trainer.is_active = is_active

            result = await self.db.execute(
                select(User).where(
                    User.email == trainer.email,
                    User.role == "trainer",
                )
            )

            user = result.scalar_one_or_none()

            if user is not None:
                user.is_active = is_active

            await self.db.commit()

            result = await self.db.execute(
                select(Trainer)
                .options(selectinload(Trainer.resume))
                .where(Trainer.trainer_id == trainer_id)
            )

            trainer = result.scalar_one_or_none()

            return trainer

        except Exception:
            await self.db.rollback()
            raise


    async def get_trainer_by_email(self, email: str) -> Trainer | None:

        result = await self.db.execute(
            select(Trainer)
            .options(selectinload(Trainer.resume))
            .where(Trainer.email == email)
        )

        trainer = result.scalar_one_or_none()

        return trainer

    async def get_trainer_by_phone(self, phone_number: str) -> Trainer | None:

        result = await self.db.execute(
            select(Trainer).where(Trainer.phone_number == phone_number)
        )

        trainer = result.scalar_one_or_none()

        return trainer
