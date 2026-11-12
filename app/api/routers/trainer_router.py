from fastapi import APIRouter, Depends, status

from app.api.dependencies.trainer_dependencies import get_trainer_service
from app.schemas.trainer import (
    TrainerCreate,
    TrainerResponse,
    TrainerUpdate,
)
from app.services.implementations.trainer_service import TrainerServiceImpl

router = APIRouter(
    prefix="/trainers",
    tags=["Trainers"],
)


@router.post(
    "/",
    response_model=TrainerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_trainer(
    trainer_data: TrainerCreate,
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.create_trainer(trainer_data)

    return trainer


@router.get(
    "/",
    response_model=list[TrainerResponse],
)
async def get_all_trainers(
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainers = await service.get_all_trainers()

    return trainers


@router.get(
    "/{trainer_id}",
    response_model=TrainerResponse,
)
async def get_trainer_by_id(
    trainer_id: int,
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.get_trainer_by_id(trainer_id)

    return trainer


@router.patch(
    "/{trainer_id}",
    response_model=TrainerResponse,
)
async def update_trainer(
    trainer_id: int,
    trainer_data: TrainerUpdate,
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.update_trainer(
        trainer_id,
        trainer_data,
    )

    return trainer


@router.patch(
    "/{trainer_id}/deactivate",
    response_model=TrainerResponse,
)
async def deactivate_trainer(
    trainer_id: int,
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.update_trainer_status(
        trainer_id,
        False,
    )

    return trainer


@router.patch(
    "/{trainer_id}/activate",
    response_model=TrainerResponse,
)
async def activate_trainer(
    trainer_id: int,
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.update_trainer_status(
        trainer_id,
        True,
    )

    return trainer
