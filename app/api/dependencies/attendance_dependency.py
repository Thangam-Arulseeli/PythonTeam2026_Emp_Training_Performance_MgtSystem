from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.batch_dependencies import get_batch_repository
from app.api.dependencies.employee import get_employee_repository
from app.api.dependencies.enrollment_dependencies import get_enrollment_repository
from app.api.dependencies.trainer_dependencies import get_trainer_repository
from app.database import get_session
from app.repositories.implementations import (
    AttendanceRecordRepository,
    AttendanceSessionRepository,
)
from app.repositories.interfaces import (
    AttendanceRecordRepositoryInterface,
    AttendanceSessionRepositoryInterface,
    BatchInterface,
    EmployeeRepositoryInterface,
    EnrollmentRepositoryInterface,
)
from app.repositories.interfaces import TrainerRepository as TrainerRepositoryInterface
from app.services.implementations import (
    AttendanceRecordService,
    AttendanceSessionService,
)
from app.services.interfaces import (
    AttendanceRecordServiceInterface,
    AttendanceSessionServiceInterface,
)


def get_attendance_session_repository(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AttendanceSessionRepositoryInterface:
    return AttendanceSessionRepository(db)


def get_attendance_record_repository(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AttendanceRecordRepositoryInterface:
    return AttendanceRecordRepository(db)


def get_attendance_session_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[
        AttendanceSessionRepositoryInterface,
        Depends(get_attendance_session_repository),
    ],
    batch_repository: Annotated[BatchInterface, Depends(get_batch_repository)],
    trainer_repository: Annotated[
        TrainerRepositoryInterface, Depends(get_trainer_repository)
    ],
    employee_repository: Annotated[
        EmployeeRepositoryInterface, Depends(get_employee_repository)
    ],
    enrollment_repository: Annotated[
        EnrollmentRepositoryInterface, Depends(get_enrollment_repository)
    ],
    record_repository: Annotated[
        AttendanceRecordRepositoryInterface,
        Depends(get_attendance_record_repository),
    ],
) -> AttendanceSessionServiceInterface:

    return AttendanceSessionService(
        db,
        repository,
        batch_repository,
        trainer_repository,
        employee_repository,
        enrollment_repository,
        record_repository,
    )


def get_attendance_record_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[
        AttendanceRecordRepositoryInterface,
        Depends(get_attendance_record_repository),
    ],
    session_repository: Annotated[
        AttendanceSessionRepositoryInterface,
        Depends(get_attendance_session_repository),
    ],
    trainer_repository: Annotated[
        TrainerRepositoryInterface, Depends(get_trainer_repository)
    ],
    enrollment_repository: Annotated[
        EnrollmentRepositoryInterface, Depends(get_enrollment_repository)
    ],
    employee_repository: Annotated[
        EmployeeRepositoryInterface, Depends(get_employee_repository)
    ],
) -> AttendanceRecordServiceInterface:

    return AttendanceRecordService(
        db,
        repository,
        session_repository,
        trainer_repository,
        enrollment_repository,
        employee_repository,
    )
