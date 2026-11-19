from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.models.performance_evaluation import PerformanceEvaluationStatus


class PerformancePreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    enrollment_id: int
    employee_id: int
    employee_name: str
    employee_email: str
    batch_id: int
    batch_name: str
    assessment_score_pct: Decimal
    total_assessments_assigned: int
    total_assessments_completed: int
    attendance_pct: Decimal
    total_sessions_conducted: int
    total_sessions_attended: int


class PerformanceEvaluationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    enrollment_id: int = Field(
        ...,
        ge=1,
        description="trainee enrollment ID",
    )
    communication_score: Decimal = Field(
        ...,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Score between 0.00 and 100.00 for communication skills",
    )
    behaviour_score: Decimal = Field(
        ...,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Score between 0.00 and 100.00 for behaviour",
    )
    teamwork_score: Decimal = Field(
        ...,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Score between 0.00 and 100.00 for collaboration and teamwork",
    )
    status: PerformanceEvaluationStatus = Field(
        default=PerformanceEvaluationStatus.DRAFT,
        description="'draft' to save progress or 'completed' to finalize",
    )
    feedback: str | None = Field(
        default=None,
        description="review remarks and recommendations",
    )


class PerformanceEvaluationUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    communication_score: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Score between 0.00 and 100.00",
    )
    behaviour_score: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Score between 0.00 and 100.00",
    )
    teamwork_score: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Score between 0.00 and 100.00",
    )
    status: PerformanceEvaluationStatus | None = Field(
        default=None,
        description="'draft' or 'completed'",
    )
    feedback: str | None = Field(
        default=None,
        description="Updated remarks and feedback",
    )


class PerformanceEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enrollment_id: int
    evaluator_id: int
    assessment_score_pct: Decimal
    attendance_pct: Decimal
    communication_score: Decimal
    behaviour_score: Decimal
    teamwork_score: Decimal
    final_score: Decimal
    grade: str
    is_certified: bool
    status: PerformanceEvaluationStatus
    feedback: str | None = None
    evaluated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class PerformanceEvaluationDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enrollment_id: int
    evaluator_id: int
    employee_id: int
    employee_name: str
    employee_email: str
    batch_id: int
    batch_name: str
    assessment_score_pct: Decimal
    attendance_pct: Decimal
    communication_score: Decimal
    behaviour_score: Decimal
    teamwork_score: Decimal
    final_score: Decimal
    grade: str
    is_certified: bool
    status: PerformanceEvaluationStatus
    feedback: str | None = None
    evaluated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
