from abc import ABC, abstractmethod
from datetime import date

from app.models.batch import Batch


class BatchInterface(ABC):
    @abstractmethod
    async def create(self, data: dict[str, object]) -> Batch:
        """Persist a batch from its field dictionary."""

    @abstractmethod
    async def get_by_id(self, batch_id: int) -> Batch | None:
        """Return a batch by ID, or None when it does not exist."""

    @abstractmethod
    async def get_all(
        self,
        skip: int,
        limit: int,
        status: str | None = None,
        is_active: bool = True,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[list[Batch], int]:
        """Return a batch page filtered by date range, status, and active state."""

    @abstractmethod
    async def get_by_course(self, course_id: int) -> list[Batch]:
        """Return all batches assigned to a course."""

    @abstractmethod
    async def get_by_trainer(self, trainer_id: int) -> list[Batch]:
        """Return all batches assigned to a trainer."""

    @abstractmethod
    async def update(self, batch: Batch, data: dict[str, object]) -> Batch:
        """Apply the supplied fields to a persisted batch."""

    @abstractmethod
    async def update_status(self, batch: Batch, status: str) -> Batch:
        """Set a batch's status and persist the change."""

    @abstractmethod
    async def set_active(self, batch: Batch, is_active: bool) -> Batch:
        """Set whether a batch is active and persist the change."""

    @abstractmethod
    async def trainer_exists(self, trainer_id: int) -> bool:
        """Check whether a trainer exists with the given ID."""
