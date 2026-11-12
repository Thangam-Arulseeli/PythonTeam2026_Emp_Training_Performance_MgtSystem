from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrainerResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resume_id: int
    trainer_id: int
    file_name: str
    file_path: str
    uploaded_at: datetime
