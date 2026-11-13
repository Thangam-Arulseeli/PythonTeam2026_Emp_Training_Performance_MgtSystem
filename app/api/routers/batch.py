from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_user, require_roles
from app.api.dependencies.service_dependencies import get_batch_service
from app.schemas.batchSchema import (
    BatchCreate,
    BatchListResponse,
    BatchResponse,
    BatchUpdate,
)
from app.services.batch_service import BatchService

router = APIRouter(
    prefix="/batches",
    tags=["Batches"],
)


@router.post(
    "/",
    response_model=BatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new batch",
)
async def create_batch(
    payload: BatchCreate,
    current_user=Depends(require_roles("admin")),
    service: BatchService = Depends(get_batch_service),
):
    """Create a batch after validating its course and trainer; admin only."""
    return await service.create_batch(payload)


@router.get(
    "/",
    response_model=BatchListResponse,
    summary="Get paginated list of all batches",
)
async def list_batches(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user=Depends(get_current_user),
    service: BatchService = Depends(get_batch_service),
):
    """Return a paginated list of batches."""
    return await service.list_batches(page=page, size=size)


@router.get(
    "/course/{course_id}",
    response_model=BatchListResponse,
    summary="Get all batches for a specific course",
)
async def get_batches_by_course(
    course_id: int,
    current_user=Depends(get_current_user),
    service: BatchService = Depends(get_batch_service),
):
    """Return all batches assigned to the requested course."""
    return await service.get_batches_by_course(course_id)


@router.get(
    "/trainer/{trainer_id}",
    response_model=BatchListResponse,
    summary="Get all batches assigned to a trainer",
)
async def get_batches_by_trainer(
    trainer_id: int,
    current_user=Depends(require_roles("admin", "trainer")),
    service: BatchService = Depends(get_batch_service),
):
    """Return batches assigned to a trainer; admins and trainers may access it."""
    return await service.get_batches_by_trainer(trainer_id)


@router.get(
    "/{batch_id}",
    response_model=BatchResponse,
    summary="Get a batch by ID",
)
async def get_batch(
    batch_id: int,
    current_user=Depends(get_current_user),
    service: BatchService = Depends(get_batch_service),
):
    """Return the batch with the requested identifier."""
    return await service.get_batch(batch_id)


@router.put(
    "/{batch_id}",
    response_model=BatchResponse,
    summary="Update a batch",
)
async def update_batch(
    batch_id: int,
    payload: BatchUpdate,
    current_user=Depends(require_roles("admin")),
    service: BatchService = Depends(get_batch_service),
):
    """Update the supplied batch fields; access is restricted to administrators."""
    return await service.update_batch(batch_id, payload)


@router.delete(
    "/{batch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a batch",
)
async def delete_batch(
    batch_id: int,
    current_user=Depends(require_roles("admin")),
    service: BatchService = Depends(get_batch_service),
):
    """Delete the requested batch; access is restricted to administrators."""
    await service.delete_batch(batch_id)
