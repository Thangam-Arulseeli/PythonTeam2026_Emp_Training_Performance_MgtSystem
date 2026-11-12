from fastapi import HTTPException, status

from app.repositories.interfaces.trainer_repository import TrainerRepository
from app.schemas.trainer import (
    TrainerCreate,
    TrainerResponse,
    TrainerUpdate,
)
from app.services.interfaces.trainer_service import TrainerService


class TrainerServiceImpl(TrainerService):

    def __init__(self, repository: TrainerRepository):
        self.repository = repository

    async def create_trainer(
        self,
        trainer_data: TrainerCreate,
    ) -> TrainerResponse:

        trainer = await self.repository.create_trainer(
            trainer_data.model_dump()
        )

        return trainer

    async def get_all_trainers(self) -> list[TrainerResponse]:

        trainers = await self.repository.get_all_trainers()

        return trainers

    async def get_trainer_by_id(
        self,
        trainer_id: int,
    ) -> TrainerResponse:

        trainer = await self.repository.get_trainer_by_id(trainer_id)

        if trainer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found",
            )

        return trainer

    async def update_trainer(
        self,
        trainer_id: int,
        trainer_data: TrainerUpdate,
    ) -> TrainerResponse:

        update_data = trainer_data.model_dump(exclude_unset=True)

        trainer = await self.repository.update_trainer(
            trainer_id,
            update_data,
        )

        if trainer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found",
            )

        return trainer

    async def update_trainer_status(
        self,
        trainer_id: int,
        is_active: bool,
    ) -> TrainerResponse:

        trainer = await self.repository.update_trainer_status(
            trainer_id,
            is_active,
        )

        if trainer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found",
            )

        return trainer