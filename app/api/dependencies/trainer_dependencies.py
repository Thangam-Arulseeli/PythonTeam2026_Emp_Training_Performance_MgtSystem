from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.implementations.trainer_repository import (
    TrainerRepositoryImpl,
)
from app.services.implementations.trainer_service import TrainerServiceImpl


def get_trainer_repository(
    db: AsyncSession = Depends(get_session),
):
    return TrainerRepositoryImpl(db)


def get_trainer_service(
    repository: TrainerRepositoryImpl = Depends(get_trainer_repository),
):
    return TrainerServiceImpl(repository)
