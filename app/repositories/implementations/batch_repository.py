
from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch import Batch
from app.models.trainer import Trainer
from app.repositories.interfaces.batch_interface import BatchInterface


class BatchRepository(BatchInterface):

    def __init__(self, db: AsyncSession) -> None:
        """Create the batch repository for the supplied async database session."""
        self.db = db

    async def create(self, data: dict[str, object]) -> Batch:
        """Insert a batch, commit the transaction, and refresh its database fields."""
        batch = Batch(**data)
        self.db.add(batch)
        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def get_by_id(self, batch_id: int) -> Batch | None:
        """Return a batch by primary key, or None when it does not exist."""
        return await self.db.get(Batch, batch_id)

    async def get_all(
        self,
        skip: int,
        limit: int,
        status: str | None = None,
        is_active: bool = True,
    ) -> tuple[list[Batch], int]:
        """Return a page and count filtered by completion status and active state."""
        stmt = select(Batch).where(Batch.is_active.is_(is_active))
        if status is not None:
            stmt = stmt.where(Batch.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar_one() or 0

        batches_stmt = (
            stmt.order_by(Batch.start_date.desc()).offset(skip).limit(limit)
        )
        batches_res = await self.db.execute(batches_stmt)
        batches = batches_res.scalars().all()
        return list(batches), total

    async def get_by_course(self, course_id: int) -> list[Batch]:
        """Return active batches for a course ordered by start date."""
        stmt = (
            select(Batch)
            .where(Batch.course_id == course_id, Batch.is_active.is_(True))
            .order_by(Batch.start_date)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_trainer(self, trainer_id: int) -> list[Batch]:
        """Return active batches assigned to a trainer ordered by start date."""
        stmt = (
            select(Batch)
            .where(Batch.trainer_id == trainer_id, Batch.is_active.is_(True))
            .order_by(Batch.start_date)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update(self, batch: Batch, data: dict[str, object]) -> Batch:
        """Apply supplied fields to a batch, commit, and refresh it."""
        for key, value in data.items():
            setattr(batch, key, value)

        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def update_status(self, batch: Batch, status: str) -> Batch:
        """Set the batch status, commit the transaction, and refresh the record."""
        batch.status = status
        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def set_active(self, batch: Batch, is_active: bool) -> Batch:
        """Update a batch's active state, commit, and refresh the record."""
        batch.is_active = is_active
        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def trainer_exists(self, trainer_id: int) -> bool:
        """Return whether a trainer exists with the given primary key."""
        stmt = select(exists().where(Trainer.trainer_id == trainer_id))
        res = await self.db.execute(stmt)
        return bool(res.scalar())

