from abc import ABC, abstractmethod

from app.schemas.trainer import TrainerCreate, TrainerResponse, TrainerUpdate


class TrainerService(ABC):
    @abstractmethod
    async def create_trainer(
        self,
        trainer_data: TrainerCreate,
    ) -> TrainerResponse:
        pass

    @abstractmethod
    async def get_all_trainers(self) -> list[TrainerResponse]:
        pass

    @abstractmethod
    async def get_trainer_by_id(
        self,
        trainer_id: int,
    ) -> TrainerResponse:
        pass

    @abstractmethod
    async def update_trainer(
        self,
        trainer_id: int,
        trainer_data: TrainerUpdate,
    ) -> TrainerResponse:
        pass

    @abstractmethod
    async def update_trainer_status(
        self,
        trainer_id: int,
        is_active: bool,
    ) -> TrainerResponse:
        pass
