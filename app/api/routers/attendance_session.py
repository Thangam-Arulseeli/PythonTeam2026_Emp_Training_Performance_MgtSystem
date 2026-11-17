from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_attance_session_service, require_roles
from app.models import User
from app.schemas import (
    AttendanceSessionCreate,
    AttendanceSessionFilter,
    AttendanceSessionUpdate,
)
from app.services.interfaces import AttendanceSessionServiceInterface

router = APIRouter(prefix="/api/attendance/session", tags=["Attendance Session"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_session(
    data: AttendanceSessionCreate,
    user: Annotated[User, Depends(require_roles("trainer", "admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attance_session_service)
    ],
):
    return await service.create_session(data, user)


@router.patch("/{session_id}/update-session")
async def update_session(
    session_id: int,
    data: AttendanceSessionUpdate,
    user: Annotated[User, Depends(require_roles("trainer", "admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attance_session_service)
    ],
):
    return await service.update_session(session_id, data, user)


@router.get("/")
async def get_all_sessions(
    user: Annotated[User, Depends(require_roles("employee", "trainer", "admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attance_session_service)
    ],
    filters: Annotated[AttendanceSessionFilter, Depends()],
):
    return await service.get_all_sessions(user, filters)


@router.get("/{session_id}")
async def get_session_by_id(
    session_id: int,
    user: Annotated[User, Depends(require_roles("employee", "trainer", "admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attance_session_service)
    ],
):
    return await service.get_session_by_id(session_id, user)


@router.get("/{trainer_id}/trainer")
async def get_session_by_trainer_id(
    trainer_id: int,
    user: Annotated[User, Depends(require_roles("admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attance_session_service)
    ],
):
    return service.get_by_trainer_id(trainer_id) 
