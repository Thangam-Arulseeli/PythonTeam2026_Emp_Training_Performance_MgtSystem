from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime, date

from app.models.assessment import AssessmentType


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
    assessment_type: AssessmentType = Field(
        description=f"Assement types: {tuple(typ.value for typ in AssessmentType)}"
    )
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

    @model_validator(mode="after")
    def validate_mark(self):
        if self.pass_mark > self.total_mark:
            raise ValueError("pass mark cannot be greater than total mark")

        return self


class AssessmentPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    batch_id: int | None = Field(description="Active Batch's ID", default=None)
    title: str | None = Field(description="Title for the Assessment", min_length=5)
    description: str | None = Field(
        description="Description about the Assessment", min_length=5, default=None
    )
    assessment_type: AssessmentType | None = Field(
        description=f"Assement types: {tuple(typ.value for typ in AssessmentType)}",
        default=None,
    )
    scheduled_date_time: datetime | None = Field(
        description="Assessment schedule date (must be within the duration of corresponding batch) ",
        default=None,
    )
    total_mark: Decimal | None = Field(
        description="Total marks for the assessment",
        max_digits=5,
        decimal_places=2,
        ge=10,
        default=None,
    )
    pass_mark: Decimal | None = Field(
        description="Minimum mark required to pass the assessment.",
        ge=0,
        max_digits=5,
        decimal_places=2,
        default=None,
    )


class AssessmentActivation(BaseModel):
    is_active: bool


class AssessmentFilterParams(BaseModel):
    page: int = Field(default=1)
    limit: int = Field(default=5)
    batch_id: int | None = None
    title: str | None = None
    assessment_type: AssessmentType | None = None
    pass_mark: Decimal | None = None
    total_mark: Decimal | None = None
    scheduled_date: date | None = None
    is_active: bool | None = None


class AssessmentListResponse(BaseModel):
    assessments: list[AssessmentResponse]
    total: int
    page: int
    limit: int
