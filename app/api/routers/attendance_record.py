from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_attendance_record_service, require_roles
from app.models import User
from app.schemas import (
    AttendanceRecordCreate,
    AttendanceRecordResponse,
    AttendanceRecordUpdate,
)
from app.services.interfaces import AttendanceRecordServiceInterface

router = APIRouter(prefix="/api/attendance/record", tags=["Attendance Record"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=AttendanceRecordResponse
)
async def create_record(
    data: AttendanceRecordCreate,
    user: Annotated[User, Depends(require_roles("trainer", "admin"))],
    service: Annotated[
        AttendanceRecordServiceInterface, Depends(get_attendance_record_service)
    ],
):
    return await service.create_record(data, user)


@router.get("/my-attendance", response_model=list[AttendanceRecordResponse])
async def get_user_attendance(
    user: Annotated[User, Depends(require_roles("employee"))],
    service: Annotated[
        AttendanceRecordServiceInterface, Depends(get_attendance_record_service)
    ],
    limit: int = Query(ge=1, le=100, default=20),
    offset: int = Query(ge=0, default=0),
):
    return await service.get_user_attendance_records(user, limit, offset)


@router.get(
    "/{session_id}/records",
    summary="get all attendance record of a session",
    response_model=list[AttendanceRecordResponse],
)
async def get_records_by_session_id(
    session_id: int,
    user: Annotated[User, Depends(require_roles("trainer", "admin"))],
    service: Annotated[
        AttendanceRecordServiceInterface, Depends(get_attendance_record_service)
    ],
):
    return await service.get_records_by_session_id(session_id, user)


@router.get("/{record_id}", response_model=AttendanceRecordResponse)
async def get_record_by_id(
    record_id: int,
    user: Annotated[User, Depends(require_roles("trainer", "admin"))],
    service: Annotated[
        AttendanceRecordServiceInterface, Depends(get_attendance_record_service)
    ],
):
    return await service.get_record_by_id(record_id, user)


@router.patch("/{record_id}", response_model=AttendanceRecordResponse)
async def update_record(
    record_id: int,
    data: AttendanceRecordUpdate,
    user: Annotated[User, Depends(require_roles("trainer", "admin"))],
    service: Annotated[
        AttendanceRecordServiceInterface, Depends(get_attendance_record_service)
    ],
):
    return await service.update_record_status(record_id, data.status, user)
