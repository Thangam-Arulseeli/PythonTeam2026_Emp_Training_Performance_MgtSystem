from abc import ABC, abstractmethod

from app.schemas.batchSchema import (
    BatchCreate,
    BatchListResponse,
    BatchResponse,
    BatchStatus,
    BatchStatusUpdate,
    BatchUpdate,
)


class BatchService(ABC):
    @abstractmethod
    async def list_batches(
        self,
        page: int = 1,
        size: int = 10,
        status: BatchStatus | None = None,
        is_active: bool = True,
    ) -> BatchListResponse: ...

    @abstractmethod
    async def create_batch(self, payload: BatchCreate) -> BatchResponse: ...

    @abstractmethod
    async def get_batch(self, batch_id: int) -> BatchResponse: ...

    @abstractmethod
    async def update_batch(
        self, batch_id: int, payload: BatchUpdate
    ) -> BatchResponse: ...

    @abstractmethod
    async def update_batch_status(
        self, batch_id: int, payload: BatchStatusUpdate
    ) -> BatchResponse: ...

    @abstractmethod
    async def delete_batch(self, batch_id: int) -> None: ...

    @abstractmethod
    async def activate_batch(self, batch_id: int) -> BatchResponse: ...

    @abstractmethod
    async def get_batches_by_course(self, course_id: int) -> BatchListResponse: ...

    @abstractmethod
    async def get_batches_by_trainer(self, trainer_id: int) -> BatchListResponse: ...
