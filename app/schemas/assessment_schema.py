from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime

from app.models.assessment import ASSESSMENT_TYPE


class AssessmentResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    title: str
    description: str | None
    assessment_type: str
    scheduled_date_time: datetime
    total_mark: Decimal | None
    pass_mark: Decimal | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AssessmentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    batch_id: int = Field(description="Active Batch's ID")
    title: str = Field(description="Title for the Assessment", min_length=5)
    description: str = Field(
        description="Description about the Assessment",
        default="No description provided.",
        min_length=5,
    )
    assessment_type: str = Field(description=f"Assement types: {ASSESSMENT_TYPE}")
    scheduled_date_time: datetime = Field(
        description="Assessment schedule date (must be within the duration of corresponding batch) "
    )
    total_mark: Decimal = Field(
        description="Total marks for the assessment",
        max_digits=5,
        decimal_places=2,
        ge=10,
    )
    pass_mark: Decimal = Field(
        description="Minimum mark required to pass the assessment.",
        ge=0,
        max_digits=5,
        decimal_places=2,
    )

    @field_validator("assessment_type")
    @classmethod
    def validate_assessment_type(cls, value: str):
        if value not in ASSESSMENT_TYPE:
            raise ValueError(
                f"Unsupported Assement type, supported types : {ASSESSMENT_TYPE}"
            )

        return value

    @model_validator(mode="after")
    def validate_mark(self):
        if self.pass_mark > self.total_mark:
            raise ValueError("pass mark cannot be greater than total mark")

        return self


class AssessmentPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    batch_id: int | None = Field(description="Active Batch's ID")
    title: str | None = Field(description="Title for the Assessment", min_length=5)
    description: str | None = Field(
        description="Description about the Assessment",
        min_length=5,
    )
    assessment_type: str | None = Field(
        description=f"Assement types: {ASSESSMENT_TYPE}"
    )
    scheduled_date_time: datetime | None = Field(
        description="Assessment schedule date (must be within the duration of corresponding batch) "
    )
    total_mark: Decimal | None = Field(
        description="Total marks for the assessment",
        max_digits=5,
        decimal_places=2,
        ge=10,
    )
    pass_mark: Decimal | None = Field(
        description="Minimum mark required to pass the assessment.",
        ge=0,
        max_digits=5,
        decimal_places=2,
    )

    @field_validator("assessment_type")
    @classmethod
    def validate_assessment_type(cls, value: str):
        if value not in ASSESSMENT_TYPE:
            raise ValueError(
                f"Unsupported Assement type, supported types : {ASSESSMENT_TYPE}"
            )

        return value
