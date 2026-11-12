from abc import ABC, abstractmethod

from app.models.trainer import Trainer


class TrainerRepository(ABC):

    @abstractmethod
    async def create_trainer(self, trainer_data: dict) -> Trainer:
        pass

    @abstractmethod
    async def get_all_trainers(self) -> list[Trainer]:
        pass

    @abstractmethod
    async def get_trainer_by_id(self, trainer_id: int) -> Trainer | None:
        pass

    @abstractmethod
    async def update_trainer(
        self,
        trainer_id: int,
        trainer_data: dict,
    ) -> Trainer | None:
        pass

    @abstractmethod
    async def update_trainer_status(
        self,
        trainer_id: int,
        is_active: bool,
    ) -> Trainer | None:
        pass