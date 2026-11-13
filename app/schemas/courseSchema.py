
from pydantic import BaseModel, ConfigDict, field_validator

MAX_DURATION_DAYS = 1000


class CourseCreate(BaseModel):
    course_name: str
    description: str | None = None
    course_contents: list[str] | None = None
    duration: int

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Course name cannot be empty")

        return value

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: int) -> int:
        if not 1 <= value <= MAX_DURATION_DAYS:
            raise ValueError(f"Duration must be between 1 and {MAX_DURATION_DAYS} days")

        return value


class CourseUpdate(BaseModel):
    course_name: str | None = None
    description: str | None = None
    course_contents: list[str] | None = None
    duration: int | None = None

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Course name cannot be empty")

        return value

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: int | None) -> int | None:
        if value is None:
            return value

        if not 1 <= value <= MAX_DURATION_DAYS:
            raise ValueError(f"Duration must be between 1 and {MAX_DURATION_DAYS} days")

        return value


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_name: str
    description: str | None = None
    course_contents: list[str] | None = None
    duration: int


class CourseListResponse(BaseModel):
    items: list[CourseResponse]
    total: int
    page: int
    size: int
