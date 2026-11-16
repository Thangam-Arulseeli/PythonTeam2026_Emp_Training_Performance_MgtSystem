from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.trainer_dependencies import get_trainer_repository
from app.database.session import get_session
from app.repositories.implementations.trainer_repository import (
    TrainerRepositoryImpl,
)
from app.repositories.implementations.trainer_resume_repository import (
    TrainerResumeRepositoryImpl,
)
from app.services.implementations.trainer_resume_service import (
    TrainerResumeServiceImpl,
)


def get_trainer_resume_repository(
    db: Annotated[AsyncSession, Depends(get_session)],
):
    return TrainerResumeRepositoryImpl(db)


def get_trainer_resume_service(
    trainer_repository: Annotated[
        TrainerRepositoryImpl, Depends(get_trainer_repository)
    ],
    resume_repository: Annotated[
        TrainerResumeRepositoryImpl, Depends(get_trainer_resume_repository)
    ],
):
    return TrainerResumeServiceImpl(trainer_repository, resume_repository)
