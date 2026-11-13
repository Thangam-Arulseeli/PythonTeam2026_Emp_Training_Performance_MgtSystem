from typing import List, Optional, Tuple

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch import Batch
from app.models.trainer import Trainer
from app.repositories.interfaces.batch_interface import BatchInterface


class BatchRepository(BatchInterface):

    def __init__(self, db: AsyncSession):
        """Create the batch repository for the supplied async database session."""
        self.db = db

    async def create(self, data: dict) -> Batch:
        """Insert a batch, commit the transaction, and refresh its database fields."""
        batch = Batch(**data)
        self.db.add(batch)
        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def get_by_id(self, batch_id: int) -> Optional[Batch]:
        """Return a batch by primary key, or None when it does not exist."""
        return await self.db.get(Batch, batch_id)

    async def get_all(
        self, skip: int, limit: int
    ) -> Tuple[List[Batch], int]:
        """Return a newest-first batch page and the total number of batches."""
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
        """Return batches for a course ordered by start date."""
        stmt = (
            select(Batch).where(Batch.course_id == course_id).order_by(Batch.start_date)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_trainer(self, trainer_id: int) -> List[Batch]:
        """Return batches assigned to a trainer ordered by start date."""
        stmt = (
            select(Batch)
            .where(Batch.trainer_id == trainer_id)
            .order_by(Batch.start_date)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update(self, batch: Batch, data: dict) -> Batch:
        """Apply supplied fields to a batch, commit, and refresh it."""
        for key, value in data.items():
            setattr(batch, key, value)

        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def delete(self, batch: Batch) -> None:
        """Delete a batch and commit the transaction."""
        await self.db.delete(batch)
        await self.db.commit()

    async def trainer_exists(self, trainer_id: int) -> bool:
        """Return whether a trainer exists with the given primary key."""
        stmt = select(exists().where(Trainer.trainer_id == trainer_id))
        res = await self.db.execute(stmt)
        return bool(res.scalar())

