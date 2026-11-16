from abc import ABC, abstractmethod

from app.models.trainer import Trainer


class TrainerRepository(ABC):
    @abstractmethod
    async def create_trainer(self, trainer_data: dict) -> Trainer:
        pass

    @abstractmethod
    async def get_all_trainers(
        self,
        offset: int,
        limit: int,
        specialization: str | None = None,
        min_experience: int | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> list[Trainer]:
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


    async def get_trainer_by_email(self, email: str) -> Trainer | None:
        pass

    async def get_trainer_by_phone(self, phone_number: str) -> Trainer | None:
        pass

