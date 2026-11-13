
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

DOCUMENT_TYPE = {"description": "Type of employee document"}

FILE_PATH = {
    "min_length": 1,
    "max_length": 500
}

EMPLOYEE_ID = {
    "gt": 0,
    "description": "Employee ID associated with the document"
}


DocumentType = Literal[
    "profile_picture",
    "resume"
]


class EmployeeDocumentBase(BaseModel):

    document_type: DocumentType = Field(**DOCUMENT_TYPE)
    file_path: str = Field(**FILE_PATH)

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("File path cannot be empty")

        return value


class EmployeeDocumentCreate(EmployeeDocumentBase):

    employee_id: int = Field(**EMPLOYEE_ID)


class EmployeeDocumentUpdate(BaseModel):

    document_type: DocumentType | None = Field(
        default=None,
        **DOCUMENT_TYPE
    )

    file_path: str | None = Field(
        default=None,
        **FILE_PATH
    )

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("File path cannot be empty")

        return value


class EmployeeDocumentResponse(EmployeeDocumentBase):

    document_id: int
    employee_id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EmployeeDocumentsListResponse(BaseModel):
    message: str
    employee_id: int
    documents: list[EmployeeDocumentResponse]
