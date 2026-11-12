from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.models.batch import Batch


class BatchInterface(ABC):

    @abstractmethod
    async def create(self, data: dict) -> Batch:
        pass

    @abstractmethod
    async def get_by_id(self, batch_id: int) -> Optional[Batch]:
        pass

    @abstractmethod
    async def get_all(
        self, skip: int, limit: int
    ) -> Tuple[List[Batch], int]:
        pass

    @abstractmethod
    async def get_by_course(self, course_id: int) -> List[Batch]:
        pass

    @abstractmethod
    async def get_by_trainer(self, trainer_id: int) -> List[Batch]:
        pass

    @abstractmethod
    async def update(self, batch: Batch, data: dict) -> Batch:
        pass

    @abstractmethod
    async def delete(self, batch: Batch) -> None:
        pass

    @abstractmethod
    async def trainer_exists(self, trainer_id: int) -> bool:
        pass

    @abstractmethod
    async def get_trainer_id_by_user_id(self, user_id: int) -> Optional[int]:
        pass
