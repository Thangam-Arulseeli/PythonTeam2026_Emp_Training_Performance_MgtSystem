from datetime import date
from uuid import uuid4
import pytest
from app.repositories.implementations.batch_repository import BatchRepository

@pytest.mark.asyncio
async def test_batch_repository_lifecycle(test_session, sample_course, sample_trainer):
    repo = BatchRepository(test_session)
    batch = await repo.create({'batch_name':'Batch ' + uuid4().hex[:8],
      'course_id':sample_course.id, 'trainer_id':sample_trainer.trainer_id,
      'start_date':date(2026,1,1), 'end_date':date(2026,2,1)})
    assert batch.status == 'Not Completed' and batch.is_active is True
    assert (await repo.get_by_id(batch.id)).id == batch.id
    assert await repo.trainer_exists(sample_trainer.trainer_id)
    assert not await repo.trainer_exists(-999)
    rows, total = await repo.get_all(0,10)
    assert total >= 1 and batch.id in [item.id for item in rows]
    assert batch.id in [item.id for item in await repo.get_by_course(sample_course.id)]
    assert batch.id in [item.id for item in await repo.get_by_trainer(sample_trainer.trainer_id)]
    assert (await repo.update(batch, {'batch_name':'Updated'})).batch_name == 'Updated'
    assert (await repo.update_status(batch, 'Completed')).status == 'Completed'
    assert (await repo.set_active(batch, False)).is_active is False
    rows, total = await repo.get_all(0,10,status='Completed',is_active=False)
    assert batch.id in [item.id for item in rows]
    assert (await repo.set_active(batch, True)).is_active is True

@pytest.mark.asyncio
async def test_missing_batch(test_session):
    assert await BatchRepository(test_session).get_by_id(-1) is None
