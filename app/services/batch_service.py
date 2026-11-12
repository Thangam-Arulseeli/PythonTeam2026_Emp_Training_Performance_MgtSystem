from typing import List, Optional

from app.exceptions import (
    NotFoundException,
    UnprocessableEntityException,
)

from app.repositories.interface.batch_interface import BatchInterface
from app.repositories.interface.course_interface import CourseInterface
from app.schema.batchSchema import (
    BatchCreate,
    BatchListResponse,
    BatchResponse,
    BatchUpdate,
)


class BatchService:

    def __init__(
        self,
        batch_repo: BatchInterface,
        course_repo: CourseInterface,
    ):
        self.batch_repo = batch_repo
        self.course_repo = course_repo

    async def get_batch_or_404(self, batch_id: int):
        batch = await self.batch_repo.get_by_id(batch_id)

        if not batch:
            raise NotFoundException("Batch not found")

        return batch

    async def validate_relations(self, course_id=None, trainer_id=None):
        if course_id is not None and not await self.course_repo.get_by_id(course_id):
            raise NotFoundException("Course not found")

        if trainer_id is not None and not await self.batch_repo.trainer_exists(trainer_id):
            raise NotFoundException("Trainer not found")

    @staticmethod
    def validate_dates(start_date, end_date):
        if end_date <= start_date:
            raise UnprocessableEntityException("End date must be after start date")

    @staticmethod
    def format_batch_list(
        batches: list,
        total: Optional[int] = None,
        page: int = 1,
        size: Optional[int] = None,
    ) -> BatchListResponse:
        count = total if total is not None else len(batches)
        page_size = size if size is not None else max(len(batches), 1)
        return BatchListResponse(
            items=[BatchResponse.model_validate(batch) for batch in batches],
            total=count,
            page=page,
            size=page_size,
        )

    async def list_batches(
        self, page: int = 1, size: int = 10
    ) -> BatchListResponse:
        skip = max(0, (page - 1) * size)
        items, total = await self.batch_repo.get_all(skip, size)
        return self.format_batch_list(items, total=total, page=page, size=size)

    async def create_batch(self, payload: BatchCreate) -> BatchResponse:
        await self.validate_relations(payload.course_id, payload.trainer_id)
        self.validate_dates(payload.start_date, payload.end_date)

        batch = await self.batch_repo.create(payload.model_dump())
        return BatchResponse.model_validate(batch)

    async def get_batch(self, batch_id: int) -> BatchResponse:
        batch = await self.get_batch_or_404(batch_id)
        return BatchResponse.model_validate(batch)

    async def update_batch(self, batch_id: int, payload: BatchUpdate) -> BatchResponse:
        batch = await self.get_batch_or_404(batch_id)

        data = payload.model_dump(exclude_unset=True)

        if not data:
            raise UnprocessableEntityException("No fields provided for update")

        for field in (
            "batch_name",
            "course_id",
            "trainer_id",
            "start_date",
            "end_date",
        ):
            if field in data and data[field] is None:
                raise UnprocessableEntityException(f"{field} cannot be null")

        await self.validate_relations(
            data.get("course_id"),
            data.get("trainer_id"),
        )

        start_date = data.get("start_date", batch.start_date)
        end_date = data.get("end_date", batch.end_date)

        self.validate_dates(start_date, end_date)

        updated_batch = await self.batch_repo.update(batch, data)
        return BatchResponse.model_validate(updated_batch)

    async def delete_batch(self, batch_id: int) -> None:
        batch = await self.get_batch_or_404(batch_id)
        await self.batch_repo.delete(batch)

    async def get_batches_by_course(self, course_id: int) -> BatchListResponse:
        if not await self.course_repo.get_by_id(course_id):
            raise NotFoundException("Course not found")

        batches = await self.batch_repo.get_by_course(course_id)
        return self.format_batch_list(batches)

    async def get_batches_by_trainer(self, trainer_id: int) -> BatchListResponse:
        if not await self.batch_repo.trainer_exists(trainer_id):
            raise NotFoundException("Trainer not found")

        batches = await self.batch_repo.get_by_trainer(trainer_id)
        return self.format_batch_list(batches)

