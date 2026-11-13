from abc import ABC, abstractmethod

from app.models.batch import Batch


class BatchInterface(ABC):

    @abstractmethod
    async def create(self, data: dict) -> Batch:
        """Persist a batch from its field dictionary."""
        pass

    @abstractmethod
    async def get_by_id(self, batch_id: int) -> Batch | None:
        """Return a batch by ID, or None when it does not exist."""
        pass

    @abstractmethod
    async def get_all(
        self, skip: int, limit: int
    ) -> tuple[list[Batch], int]:
        """Return a batch page and the total number of batches."""
        pass

    @abstractmethod
    async def get_by_course(self, course_id: int) -> list[Batch]:
        """Return all batches assigned to a course."""
        pass

    @abstractmethod
    async def get_by_trainer(self, trainer_id: int) -> list[Batch]:
        """Return all batches assigned to a trainer."""
        pass

    @abstractmethod
    async def update(self, batch: Batch, data: dict) -> Batch:
        """Apply the supplied fields to a persisted batch."""
        pass

    @abstractmethod
    async def delete(self, batch: Batch) -> None:
        """Delete a persisted batch."""
        pass

    @abstractmethod
    async def trainer_exists(self, trainer_id: int) -> bool:
        """Check whether a trainer exists with the given ID."""
        pass

