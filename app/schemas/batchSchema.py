from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationInfo,
    field_validator,
    model_validator,
)


class BatchCreate(BaseModel):
    batch_name: str
    course_id: int
    trainer_id: int
    start_date: date
    end_date: date

    @field_validator("batch_name")
    @classmethod
    def validate_batch_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Batch name cannot be empty")

        return value

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, value: date, info: ValidationInfo) -> date:
        start_date = info.data.get("start_date")

        if start_date and value <= start_date:
            raise ValueError("End date must be after start date")

        return value


class BatchUpdate(BaseModel):
    batch_name: str | None = None
    course_id: int | None = None
    trainer_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("batch_name")
    @classmethod
    def validate_batch_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Batch name cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_dates(self) -> "BatchUpdate":
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        return self


class BatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_name: str
    course_id: int
    trainer_id: int
    start_date: date
    end_date: date


class BatchListResponse(BaseModel):
    items: list[BatchResponse]
    total: int
    page: int
    size: int
