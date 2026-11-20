from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core import AttendanceStatus


class AttendanceRecordBase(BaseModel):
    session_id: int = Field(gt=0)
    enrollment_id: int = Field(gt=0)
    status: AttendanceStatus


class AttendanceRecordCreate(AttendanceRecordBase):
    pass


class AttendanceRecordUpdate(BaseModel):
    status: AttendanceStatus


class AttendanceRecordResponse(AttendanceRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    marked_by: int
    marked_at: datetime
    updated_at: datetime
