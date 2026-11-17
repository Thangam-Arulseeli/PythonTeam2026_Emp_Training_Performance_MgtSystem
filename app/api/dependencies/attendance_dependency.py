from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.batch_dependencies import get_batch_service
from app.api.dependencies.employee import get_employee_repository
from app.api.dependencies.trainer_dependencies import get_trainer_repository
from app.database import get_session
from app.repositories.implementations import AttendanceSessionRepository
from app.repositories.interfaces import (
    AttendanceSessionRepositoryInterface,
    EmployeeRepositoryInterface,
)
from app.repositories.interfaces import BatchInterface as BatchServiceInterface
from app.repositories.interfaces import (
    TrainerRepository as TrainerRepositoryInterface,
)
from app.services.implementations import AttendanceSessionService
from app.services.interfaces import AttendanceSessionServiceInterface


def get_attendance_session_repository(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AttendanceSessionRepositoryInterface:
    return AttendanceSessionRepository(db)


def get_attance_session_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[
        AttendanceSessionRepositoryInterface, Depends(get_attendance_session_repository)
    ],
    batch_repository: Annotated[BatchServiceInterface, Depends(get_batch_service)],
    trainer_repository: Annotated[
        TrainerRepositoryInterface, Depends(get_trainer_repository)
    ],
    employee_repository: Annotated[
        EmployeeRepositoryInterface, Depends(get_employee_repository)
    ],
) -> AttendanceSessionServiceInterface:
    return AttendanceSessionService(
        db, repository, batch_repository, trainer_repository , employee_repository
    )
