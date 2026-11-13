from typing import List, Optional

from app.exceptions import (
    NotFoundException,
    UnprocessableEntityException,
)
from app.repositories.interfaces.batch_interface import BatchInterface
from app.repositories.interfaces.course_interface import CourseInterface
from app.schemas.batchSchema import (
    BatchCreate,
    BatchListResponse,
    BatchResponse,
    BatchUpdate,
)
from app.utils.logger import logger


class BatchService:

    def __init__(
        self,
        batch_repo: BatchInterface,
        course_repo: CourseInterface,
    ):
        """Create the batch service with batch and course persistence interfaces."""
        self.batch_repo = batch_repo
        self.course_repo = course_repo

    async def get_batch_or_404(self, batch_id: int):
        """Load a batch by ID or raise a not-found error."""
        batch = await self.batch_repo.get_by_id(batch_id)

        if not batch:
            logger.warning("Batch not found: batch_id=%s", batch_id)
            raise NotFoundException("Batch not found")

        return batch

    async def validate_relations(self, course_id=None, trainer_id=None):
        """Confirm each supplied course and trainer ID refers to an existing record."""
        if course_id is not None and not await self.course_repo.get_by_id(course_id):
            logger.warning("Relation validation failed: Course not found id=%s", course_id)
            raise NotFoundException("Course not found")

        if trainer_id is not None and not await self.batch_repo.trainer_exists(trainer_id):
            logger.warning("Relation validation failed: Trainer not found id=%s", trainer_id)
            raise NotFoundException("Trainer not found")

    @staticmethod
    def validate_dates(start_date, end_date):
        """Require the batch end date to be later than its start date."""
        if end_date <= start_date:
            raise UnprocessableEntityException("End date must be after start date")

    @staticmethod
    def format_batch_list(
        batches: list,
        total: Optional[int] = None,
        page: int = 1,
        size: Optional[int] = None,
    ) -> BatchListResponse:
        """Convert batch records into the paginated API response shape."""
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
        """Fetch and format a page of batches with the total record count."""
        skip = max(0, (page - 1) * size)
        items, total = await self.batch_repo.get_all(skip, size)
        return self.format_batch_list(items, total=total, page=page, size=size)

    async def create_batch(self, payload: BatchCreate) -> BatchResponse:
        """Validate relationships and dates, then create and return a batch."""
        await self.validate_relations(payload.course_id, payload.trainer_id)
        self.validate_dates(payload.start_date, payload.end_date)

        batch = await self.batch_repo.create(payload.model_dump())
        logger.info("Batch created successfully: id=%s, name='%s'", batch.id, batch.batch_name)
        return BatchResponse.model_validate(batch)

    async def get_batch(self, batch_id: int) -> BatchResponse:
        """Return the requested batch or raise a not-found error."""
        batch = await self.get_batch_or_404(batch_id)
        return BatchResponse.model_validate(batch)

    async def update_batch(self, batch_id: int, payload: BatchUpdate) -> BatchResponse:
        """Validate supplied fields and relationships before updating a batch."""
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
        logger.info("Batch updated successfully: id=%s", batch_id)
        return BatchResponse.model_validate(updated_batch)

    async def delete_batch(self, batch_id: int) -> None:
        """Delete the requested batch or raise a not-found error."""
        batch = await self.get_batch_or_404(batch_id)
        await self.batch_repo.delete(batch)
        logger.info("Batch deleted successfully: id=%s", batch_id)

    async def get_batches_by_course(self, course_id: int) -> BatchListResponse:
        """Return batches for an existing course."""
        if not await self.course_repo.get_by_id(course_id):
            logger.warning("get_batches_by_course failed: Course not found id=%s", course_id)
            raise NotFoundException("Course not found")

        batches = await self.batch_repo.get_by_course(course_id)
        return self.format_batch_list(batches)

    async def get_batches_by_trainer(self, trainer_id: int) -> BatchListResponse:
        """Return batches for an existing trainer."""
        if not await self.batch_repo.trainer_exists(trainer_id):
            logger.warning("get_batches_by_trainer failed: Trainer not found id=%s", trainer_id)
            raise NotFoundException("Trainer not found")

        batches = await self.batch_repo.get_by_trainer(trainer_id)
        return self.format_batch_list(batches)
