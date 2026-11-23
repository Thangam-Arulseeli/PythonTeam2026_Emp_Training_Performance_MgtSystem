# tests/conftest.py

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.services.implementations import (
    AttendanceRecordService,
    AttendanceSessionService,
)


@pytest.fixture
def session_dependencies():
    db = AsyncMock()

    repository = AsyncMock()
    batch_repository = AsyncMock()
    trainer_repository = AsyncMock()
    employee_repository = AsyncMock()
    enrollment_repository = AsyncMock()
    record_repository = AsyncMock()

    service = AttendanceSessionService(
        db=db,
        repository=repository,
        batch_repository=batch_repository,
        trainer_repository=trainer_repository,
        employee_repository=employee_repository,
        enrollment_repository=enrollment_repository,
        record_repository=record_repository,
    )

    return SimpleNamespace(
        service=service,
        db=db,
        repository=repository,
        batch_repository=batch_repository,
        trainer_repository=trainer_repository,
        employee_repository=employee_repository,
        enrollment_repository=enrollment_repository,
        record_repository=record_repository,
    )


@pytest.fixture
def record_dependencies():
    db = AsyncMock()

    repository = AsyncMock()
    session_repository = AsyncMock()
    trainer_repository = AsyncMock()
    enrollment_repository = AsyncMock()
    employee_repository = AsyncMock()

    service = AttendanceRecordService(
        db=db,
        repository=repository,
        session_repository=session_repository,
        trainer_repository=trainer_repository,
        enrollment_repository=enrollment_repository,
        employee_repository=employee_repository,
    )

    return SimpleNamespace(
        service=service,
        db=db,
        repository=repository,
        session_repository=session_repository,
        trainer_repository=trainer_repository,
        enrollment_repository=enrollment_repository,
        employee_repository=employee_repository,
    )
