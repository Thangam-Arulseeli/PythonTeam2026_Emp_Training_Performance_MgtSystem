from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.models.assessment_result import AssessmentResultStatus


class AssessmentResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assessment_id: int
    enrollment_id: int
    status: AssessmentResultStatus
    mark: Decimal | None
    grade: str | None
    feedback: str | None
    file_name: str | None
    file_path: str | None
    submitted_date_time: datetime | None
    evaluated_date_time: datetime | None
    created_at: datetime
    updated_at: datetime


class AssessmentAssignResponse(BaseModel):
    assessment_id: int
    batch_id: int
    assigned_count: int
    skipped_count: int
    message: str
    assigned_enrollment_ids: list[int]
