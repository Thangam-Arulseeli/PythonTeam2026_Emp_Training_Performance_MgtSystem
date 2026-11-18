from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

EnrollmentStatus = Literal[
    "enrolled",
    "paused",
    "cancelled",
    "completed"
]

class EnrollmentCreate(BaseModel):
    employee_id : int = Field(gt=0)
    batch_id : int = Field(gt=0)

class EnrollmentStatusUpdate(BaseModel):
    status : Literal[
        "enrolled",
        "paused",
        "cancelled",
        "completed"
    ]
    remarks : str | None = Field(
        default= None,
        max_length=1500
    )

    @field_validator("remarks")
    @classmethod
    def validate_remarks(cls, value: str | None) -> str | None:
        if value is not None:
            value= value.strip()

            if not value:
                return None

        return value

class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    enrollment_id : int 
    employee_id : int
    batch_id : int
    enrollment_date : datetime
    status : EnrollmentStatus
    status_update_date : datetime | None = None
    remarks : str|None = None
    created_at : datetime
    updated_at : datetime

class EnrollmentListResponse(BaseModel):
    items: list[EnrollmentResponse]
    total: int
    page: int
    size: int
        

