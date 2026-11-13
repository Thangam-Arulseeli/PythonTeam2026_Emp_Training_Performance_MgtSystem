from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependencies.trainer_resume_dependencies import (
    get_trainer_resume_service,
)
from app.schemas.trainer_resume import TrainerResumeResponse
from app.services.implementations.trainer_resume_service import (
    TrainerResumeServiceImpl,
)

router = APIRouter(
    prefix="/trainers",
    tags=["Trainer Resumes"],
)


@router.post(
    "/{trainer_id}/resume",
    response_model=TrainerResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_trainer_resume(
    trainer_id: int,
    file: UploadFile = File(...),
    service: TrainerResumeServiceImpl = Depends(get_trainer_resume_service),
):
    return await service.upload_trainer_resume(trainer_id, file)
