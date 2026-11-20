from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

BatchStatus = Literal["completed", "not_completed"]


class BatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_name: str
    course_id: int
    trainer_id: int
    start_date: date

    @field_validator("batch_name")
    @classmethod
    def validate_batch_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Batch name cannot be empty")

        return value


class BatchUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_name: str | None = None
    course_id: int | None = None
    trainer_id: int | None = None

    @field_validator("batch_name")
    @classmethod
    def validate_batch_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Batch name cannot be empty")

        return value


class BatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_name: str
    course_id: int
    trainer_id: int
    start_date: date
    end_date: date
    end_date_remark: str | None = None
    status: BatchStatus
    is_active: bool


class BatchStatusUpdate(BaseModel):
    status: BatchStatus


class BatchEndDateUpdate(BaseModel):
    end_date: date
    remark: str = Field(min_length=1, max_length=1000)

    @field_validator("remark")
    @classmethod
    def validate_remark(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Remark cannot be empty")
        return value


class BatchListResponse(BaseModel):
    items: list[BatchResponse]
    total: int
    page: int
    size: int
