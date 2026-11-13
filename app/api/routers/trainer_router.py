from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import require_roles
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
    current_user=Depends(require_roles("admin")),
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.create_trainer(trainer_data)

    return trainer


@router.get("/", response_model=list[TrainerResponse])
async def get_all_trainers(
    offset: int = 0,
    limit: int = 10,
    specialization: str | None = None,
    min_experience: int | None = Query(default=None, ge=0),
    is_active: bool | None = None,
    search_name: str | None = None,
    current_user=Depends(require_roles("admin")),
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainers = await service.get_all_trainers(
        offset,
        limit,
        specialization,
        min_experience,
        is_active,
        search_name,
    )

    return trainers




@router.get(
    "/me",
    response_model=TrainerResponse,
)
async def get_my_trainer_details(
    current_user=Depends(require_roles("trainer")),
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.get_my_trainer_details(
        current_user.email
    )

    return trainer



@router.get(
    "/{trainer_id}",
    response_model=TrainerResponse,
)
async def get_trainer_by_id(
    trainer_id: int,
    current_user=Depends(require_roles("admin")),
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
    current_user=Depends(require_roles("admin")),
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.update_trainer(
        trainer_id,
        trainer_data,
    )

    return trainer


@router.patch(
    "/{trainer_id}/inactive",
    response_model=TrainerResponse,
)
async def deactivate_trainer(
    trainer_id: int,
    current_user=Depends(require_roles("admin")),
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.update_trainer_status(
        trainer_id,
        False,
    )

    return trainer


@router.patch(
    "/{trainer_id}/active",
    response_model=TrainerResponse,
)
async def activate_trainer(
    trainer_id: int,
    current_user=Depends(require_roles("admin")),
    service: TrainerServiceImpl = Depends(get_trainer_service),
):
    trainer = await service.update_trainer_status(
        trainer_id,
        True,
    )

    return trainer


