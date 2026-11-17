from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core import AttendanceSessionStatus


class AttendanceSessionBase(BaseModel):
    session_date: date
    start_time: time
    end_time: time
    topic: str = Field(
        min_length=2,
        max_length=200,
    )
    status: AttendanceSessionStatus
    description: str | None = None

    @model_validator(mode="after")
    def validate_session_time(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be later than start time")
        return self


class AttendanceSessionCreate(AttendanceSessionBase):
    batch_id: int = Field(gt=0)


class AttendanceSessionUpdate(BaseModel):
    session_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None

    topic: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None
    status: AttendanceSessionStatus | None = None

    @model_validator(mode="after")
    def validate_session_time(self):
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time <= self.start_time
        ):
            raise ValueError("End time must be later than start time")
        return self


class AttendanceSessionResponse(AttendanceSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    status: AttendanceSessionStatus
    created_at: datetime
    updated_at: datetime


class AttendanceSessionFilter(BaseModel):
    batch_id: int | None = Field(default=None, gt=0)

    session_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None

    status: AttendanceSessionStatus | None = None

    topic: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("End date cannot be earlier than start date")

        return self