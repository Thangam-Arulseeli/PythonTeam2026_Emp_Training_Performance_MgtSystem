
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.duration import DurationUnit, duration_to_standard_units

MAX_DURATION_STANDARD_UNITS = 24_000


class CourseCreate(BaseModel):
    course_name: str
    description: str | None = None
    course_contents: list[str] | None = None
    duration_value: int = Field(ge=1)
    duration_unit: DurationUnit

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Course name cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_duration(self) -> "CourseCreate":
        normalized_value = duration_to_standard_units(
            self.duration_value, self.duration_unit
        )
        if normalized_value > MAX_DURATION_STANDARD_UNITS:
            raise ValueError(
                "Duration exceeds the maximum supported length"
            )
        return self


class CourseUpdate(BaseModel):
    course_name: str | None = None
    description: str | None = None
    course_contents: list[str] | None = None
    duration_value: int | None = Field(default=None, ge=1)
    duration_unit: DurationUnit | None = None

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Course name cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_duration(self) -> "CourseUpdate":
        if "duration_value" in self.model_fields_set and self.duration_value is None:
            raise ValueError("duration_value cannot be null")
        if "duration_unit" in self.model_fields_set and self.duration_unit is None:
            raise ValueError("duration_unit cannot be null")

        if self.duration_value is not None and self.duration_unit is not None:
            if (
                duration_to_standard_units(self.duration_value, self.duration_unit)
                > MAX_DURATION_STANDARD_UNITS
            ):
                raise ValueError("Duration exceeds the maximum supported length")
        return self


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_name: str
    description: str | None = None
    course_contents: list[str] | None = None
    duration_value: int
    duration_unit: DurationUnit


class CourseListResponse(BaseModel):
    items: list[CourseResponse]
    total: int
    page: int
    size: int
