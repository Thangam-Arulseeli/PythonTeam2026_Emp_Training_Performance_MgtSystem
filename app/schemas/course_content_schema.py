
from pydantic import BaseModel, ConfigDict


class CourseContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    filename: str
    file_path: str


class CourseContentListResponse(BaseModel):
    items: list[CourseContentResponse]
    total: int
    page: int
    size: int
