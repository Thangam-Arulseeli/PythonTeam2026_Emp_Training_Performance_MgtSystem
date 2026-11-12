from typing import List, Optional, Tuple

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch import Batch
from app.models.trainer import Trainer
from app.repositories.interface.batch_interface import BatchInterface


class BatchRepository(BatchInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Batch:
        batch = Batch(**data)
        self.db.add(batch)
        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def get_by_id(self, batch_id: int) -> Optional[Batch]:
        return await self.db.get(Batch, batch_id)

    async def get_all(
        self, skip: int, limit: int
    ) -> Tuple[List[Batch], int]:
        stmt = select(Batch)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar_one() or 0

        batches_stmt = (
            stmt.order_by(Batch.start_date.desc()).offset(skip).limit(limit)
        )
        batches_res = await self.db.execute(batches_stmt)
        batches = batches_res.scalars().all()
        return list(batches), total

    async def get_by_course(self, course_id: int) -> List[Batch]:
        stmt = (
            select(Batch).where(Batch.course_id == course_id).order_by(Batch.start_date)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_trainer(self, trainer_id: int) -> List[Batch]:
        stmt = (
            select(Batch)
            .where(Batch.trainer_id == trainer_id)
            .order_by(Batch.start_date)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update(self, batch: Batch, data: dict) -> Batch:
        for key, value in data.items():
            setattr(batch, key, value)

        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def delete(self, batch: Batch) -> None:
        await self.db.delete(batch)
        await self.db.commit()

    async def trainer_exists(self, trainer_id: int) -> bool:
        stmt = select(exists().where(Trainer.trainer_id == trainer_id))
        res = await self.db.execute(stmt)
        return bool(res.scalar())

    async def get_trainer_id_by_user_id(self, user_id: int) -> Optional[int]:
        if hasattr(Trainer, "user_id"):
            stmt = select(Trainer.trainer_id).where(getattr(Trainer, "user_id") == user_id)
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        # Fallback to direct trainer_id match until auth user_id is linked
        stmt = select(Trainer.trainer_id).where(Trainer.trainer_id == user_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
