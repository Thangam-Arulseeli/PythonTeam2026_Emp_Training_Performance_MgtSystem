from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.models.assessment import AssessmentType
from app.models.assessment_result import AssessmentResultStatus


class AssessmentResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assessment_id: int
    enrollment_id: int
    status: AssessmentResultStatus
    mark: Decimal | None = None
    grade: str | None = None
    feedback: str | None = None
    file_name: str | None = None
    file_path: str | None = None
    submitted_date_time: datetime | None = None
    evaluated_date_time: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AssessmentAssignResponse(BaseModel):
    assessment_id: int
    batch_id: int
    assigned_count: int
    skipped_count: int
    message: str
    assigned_enrollment_ids: list[int]


class TraineeAssessmentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    result_id: int
    enrollment_id: int
    status: AssessmentResultStatus
    mark: Decimal | None = None
    grade: str | None = None
    feedback: str | None = None
    file_name: str | None = None
    submitted_date_time: datetime | None = None
    evaluated_date_time: datetime | None = None

    assessment_id: int
    batch_id: int
    title: str
    description: str | None = None
    assessment_type: AssessmentType
    scheduled_date_time: datetime
    total_mark: Decimal
    pass_mark: Decimal


class AssessmentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    result_id: int
    assessment_id: int
    enrollment_id: int
    employee_id: int
    employee_name: str
    employee_email: str
    status: AssessmentResultStatus
    mark: Decimal | None = None
    grade: str | None = None
    feedback: str | None = None
    file_name: str | None = None
    submitted_date_time: datetime | None = None
    evaluated_date_time: datetime | None = None


class AssessmentGradeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    mark: Decimal = Field(
        ...,
        ge=0,
        max_digits=5,
        decimal_places=2,
        description="Mark awarded to the trainee",
    )
    grade: str | None = Field(
        default=None,
        max_length=10,
        description="Optional custom grade e.g. A+, B. Auto-derived (PASS/FAIL) if omitted.",
    )
    feedback: str | None = Field(
        default=None,
        description="Trainer remarks / feedback",
    )


class AssessmentCancelRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    reason: str | None = Field(
        default=None,
        description="Reason for cancellation / exemption",
    )
