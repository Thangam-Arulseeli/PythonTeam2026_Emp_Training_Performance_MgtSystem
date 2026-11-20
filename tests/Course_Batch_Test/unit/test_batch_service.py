from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from app.exceptions import NotFoundException, UnprocessableEntityException
from app.models.batch import Batch
from app.schemas.batchSchema import BatchCreate, BatchUpdate, BatchStatusUpdate
from app.services.implementations.batch_service import BatchServiceImpl

def batch_model():
    return Batch(id=1, batch_name='Morning', course_id=2, trainer_id=3,
                 start_date=date(2026, 1, 1), end_date=date(2026, 2, 1),
                 status='Not Completed', is_active=True)

@pytest.fixture
def repos():
    return AsyncMock(), AsyncMock()

@pytest.fixture
def service(repos):
    return BatchServiceImpl(*repos)

@pytest.mark.asyncio
async def test_create_validates_course_and_trainer(service, repos):
    batch_repo, course_repo = repos
    course_repo.get_by_id.return_value = SimpleNamespace(
        duration_value=4, duration_unit='weeks'
    )
    batch_repo.trainer_exists.return_value = True
    batch_repo.create.return_value = batch_model()
    result = await service.create_batch(BatchCreate(batch_name='Morning', course_id=2, trainer_id=3,
                                                     start_date=date(2026,1,1)))
    assert result.id == 1
    batch_repo.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_missing_course_or_trainer(service, repos):
    batch_repo, course_repo = repos
    payload = BatchCreate(batch_name='Morning', course_id=2, trainer_id=3,
                          start_date=date(2026,1,1))
    course_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundException):
        await service.create_batch(payload)
    course_repo.get_by_id.return_value = SimpleNamespace(
        duration_value=4, duration_unit='weeks'
    )
    batch_repo.trainer_exists.return_value = False
    with pytest.raises(NotFoundException):
        await service.create_batch(payload)


@pytest.mark.asyncio
async def test_list_pagination_filters(service, repos):
    repos[0].get_all.return_value = ([batch_model()], 8)
    response = await service.list_batches(page=2, size=3, status='Completed', is_active=False)
    repos[0].get_all.assert_awaited_once_with(3, 3, 'Completed', False)
    assert response.total == 8

@pytest.mark.asyncio
async def test_update_rejects_empty_and_null(service, repos):
    repos[0].get_by_id.return_value = batch_model()
    with pytest.raises(UnprocessableEntityException):
        await service.update_batch(1, BatchUpdate())
    with pytest.raises(UnprocessableEntityException):
        await service.update_batch(1, BatchUpdate(batch_name=None))

@pytest.mark.asyncio
async def test_update_status_delete_activate(service, repos):
    repo = repos[0]
    repo.get_by_id.return_value = batch_model()
    repo.update_status.return_value = batch_model()
    await service.update_batch_status(1, BatchStatusUpdate(status='Completed'))
    repo.update_status.assert_awaited_once()
    repo.set_active.return_value = batch_model()
    await service.delete_batch(1)
    repo.set_active.assert_any_await(repo.get_by_id.return_value, False)
    active = await service.activate_batch(1)
    assert active.is_active
    repo.set_active.assert_any_await(repo.get_by_id.return_value, True)

@pytest.mark.asyncio
async def test_batches_by_course_and_trainer(service, repos):
    batch_repo, course_repo = repos
    course_repo.get_by_id.return_value = object()
    batch_repo.trainer_exists.return_value = True
    batch_repo.get_by_course.return_value = [batch_model()]
    batch_repo.get_by_trainer.return_value = [batch_model()]
    assert (await service.get_batches_by_course(2)).total == 1
    assert (await service.get_batches_by_trainer(3)).total == 1
