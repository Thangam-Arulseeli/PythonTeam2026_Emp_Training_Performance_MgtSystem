from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer

EnrollmentStatus = Literal[
    "Enrolled",
    "Paused",
    "Cancelled",
    "Completed"
]

class EnrollmentCreate(BaseModel):
    employee_id : int = Field(gt=0)
    batch_id : int = Field(gt=0)

class EnrollmentStatusUpdate(BaseModel):
    status : Literal[
        "Enrolled",
        "Paused",
        "Cancelled",
        "Completed"
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

class EmployeeDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    employee_id: int
    full_name: str
    email: str

class CourseDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    course_name: str
    duration_value: int
    duration_unit: str

class TrainerDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    trainer_id : int
    trainer_name: str

class BatchDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    batch_name: str
    start_date: date
    end_date: date
    course: CourseDetails
    trainer: TrainerDetails

class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    enrollment_id : int
    enrollment_date : datetime
    status : EnrollmentStatus
    status_update_date : datetime | None = None
    remarks : str|None = None
    employee: EmployeeDetails
    batch:BatchDetails
    created_at : datetime
    updated_at : datetime

class EnrollmentListResponse(BaseModel):
    items: list[EnrollmentResponse]
    total: int
    page: int
    size: int
        

