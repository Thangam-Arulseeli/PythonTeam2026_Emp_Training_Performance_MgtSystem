from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_attendance_session_service, require_roles
from app.models import User
from app.schemas import (
    AttendanceSessionCreate,
    AttendanceSessionFilter,
    AttendanceSessionResponse,
    AttendanceSessionUpdate,
)
from app.services.interfaces import AttendanceSessionServiceInterface

router = APIRouter(prefix="/api/attendance/session", tags=["Attendance Session"])


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=AttendanceSessionResponse,
)
async def create_session(
    data: AttendanceSessionCreate,
    user: Annotated[User, Depends(require_roles("trainer", "admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attendance_session_service)
    ],
):
    return await service.create(data, user)


@router.patch(
    "/{session_id}/update-session",
    response_model=AttendanceSessionResponse,
)
async def update_session(
    session_id: int,
    data: AttendanceSessionUpdate,
    user: Annotated[User, Depends(require_roles("trainer", "admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attendance_session_service)
    ],
):
    return await service.update_session(session_id, data, user)


@router.get(
    "/",
    response_model=list[AttendanceSessionResponse],
)
async def get_all_sessions(
    user: Annotated[User, Depends(require_roles("employee", "trainer", "admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attendance_session_service)
    ],
    filters: Annotated[AttendanceSessionFilter, Depends()],
):
    return await service.get_all_sessions(user, filters)


@router.get("/my-sessions", response_model=list[AttendanceSessionResponse])
async def get_user_sessions(
    user: Annotated[User, Depends(require_roles("employee", "trainer"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attendance_session_service)
    ],
):
    return await service.get_current_user_sessions(user)


@router.get("/{session_id}", response_model=AttendanceSessionResponse)
async def get_session_by_id(
    session_id: int,
    user: Annotated[User, Depends(require_roles("employee", "trainer", "admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attendance_session_service)
    ],
):
    return await service.get_session_by_id(session_id, user)


@router.get("/{trainer_id}/trainer", response_model=list[AttendanceSessionResponse])
async def get_session_by_trainer_id(
    trainer_id: int,
    user: Annotated[User, Depends(require_roles("admin"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attendance_session_service)
    ],
):
    return await service.get_by_trainer_id(trainer_id)


@router.patch("/{session_id}/complete", response_model=AttendanceSessionResponse)
async def mark_session_complete(
    session_id: int,
    user: Annotated[User, Depends(require_roles("admin", "trainer"))],
    service: Annotated[
        AttendanceSessionServiceInterface, Depends(get_attendance_session_service)
    ],
):
    return await service.complete_session(session_id, user)
