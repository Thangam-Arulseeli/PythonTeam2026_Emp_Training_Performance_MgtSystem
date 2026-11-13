from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependencies.auth import require_roles
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


@router.get(
    "/{trainer_id}/resume",
    response_model=TrainerResumeResponse,
)
async def get_trainer_resume(
    trainer_id: int,
    current_user=Depends(require_roles("admin")),
    service: TrainerResumeServiceImpl = Depends(get_trainer_resume_service),
):
    return await service.get_trainer_resume(trainer_id)


@router.post(
    "/{trainer_id}/resume",
    response_model=TrainerResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_trainer_resume(
    trainer_id: int,
    file: UploadFile = File(...),
    current_user=Depends(require_roles("admin")),
    service: TrainerResumeServiceImpl = Depends(get_trainer_resume_service),
):
    return await service.upload_trainer_resume(trainer_id, file)
