from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependency.deps import get_batch_service
from app.schema.batchSchema import (
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
    service: BatchService = Depends(get_batch_service),
):
    return await service.create_batch(payload)


@router.get(
    "/",
    response_model=BatchListResponse,
    summary="Get paginated list of all batches",
)
async def list_batches(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: BatchService = Depends(get_batch_service),
):
    return await service.list_batches(page=page, size=size)


@router.get(
    "/course/{course_id}",
    response_model=BatchListResponse,
    summary="Get all batches for a specific course",
)
async def get_batches_by_course(
    course_id: int,
    service: BatchService = Depends(get_batch_service),
):
    return await service.get_batches_by_course(course_id)


@router.get(
    "/trainer/{trainer_id}",
    response_model=BatchListResponse,
    summary="Get all batches assigned to a trainer",
)
async def get_batches_by_trainer(
    trainer_id: int,
    service: BatchService = Depends(get_batch_service),
):
    return await service.get_batches_by_trainer(trainer_id)


@router.get(
    "/{batch_id}",
    response_model=BatchResponse,
    summary="Get a batch by ID",
)
async def get_batch(
    batch_id: int,
    service: BatchService = Depends(get_batch_service),
):
    return await service.get_batch(batch_id)


@router.put(
    "/{batch_id}",
    response_model=BatchResponse,
    summary="Update a batch",
)
async def update_batch(
    batch_id: int,
    payload: BatchUpdate,
    service: BatchService = Depends(get_batch_service),
):
    return await service.update_batch(batch_id, payload)


@router.delete(
    "/{batch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a batch",
)
async def delete_batch(
    batch_id: int,
    service: BatchService = Depends(get_batch_service),
):
    await service.delete_batch(batch_id)
