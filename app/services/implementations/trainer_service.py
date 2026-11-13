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

        existing_email = await self.repository.get_trainer_by_email(trainer_data.email)

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        existing_phone = await self.repository.get_trainer_by_phone(
            trainer_data.phone_number
        )

        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already exists",
            )

        trainer = await self.repository.create_trainer(trainer_data.model_dump())

        return trainer

    async def get_all_trainers(
        self,
        offset: int,
        limit: int,
        specialization: str | None = None,
        min_experience: int | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> list[TrainerResponse]:

        trainers = await self.repository.get_all_trainers(
            offset,
            limit,
            specialization,
            min_experience,
            is_active,
            search,
        )

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

        existing_trainer = await self.repository.get_trainer_by_id(trainer_id)

        if existing_trainer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found",
            )

        if "email" in update_data:
            existing_email = await self.repository.get_trainer_by_email(
                update_data["email"]
            )

            if existing_email and existing_email.trainer_id != trainer_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists",
                )

        if "phone_number" in update_data:
            existing_phone = await self.repository.get_trainer_by_phone(
                update_data["phone_number"]
            )

            if existing_phone and existing_phone.trainer_id != trainer_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Phone number already exists",
                )

        trainer = await self.repository.update_trainer(
            trainer_id,
            update_data,
        )

        return trainer

    async def update_trainer_status(
        self,
        trainer_id: int,
        is_active: bool,
    ) -> TrainerResponse:

        trainer = await self.repository.get_trainer_by_id(trainer_id)

        if trainer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found",
            )

        updated_trainer = await self.repository.update_trainer_status(
            trainer_id,
            is_active,
        )

        return updated_trainer



    async def get_my_trainer_details(
        self,
        email: str,
    ) -> TrainerResponse:

        trainer = await self.repository.get_trainer_by_email(email)

        if trainer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer details not found",
            )

        return trainer
    