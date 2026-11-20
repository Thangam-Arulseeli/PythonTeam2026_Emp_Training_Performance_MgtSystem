"""Every one of the nine Batch routes: success + representative negative paths."""
from datetime import date
from unittest.mock import AsyncMock
import pytest
from app.api.dependencies.batch_dependencies import get_batch_service
from app.exceptions import NotFoundException, ConflictException
from app.main import app
from app.schemas.batchSchema import BatchResponse, BatchListResponse

pytestmark = [pytest.mark.api, pytest.mark.asyncio]
ROOT = '/batches'
PAYLOAD = {'batch_name': 'Morning Class', 'course_id': 2, 'trainer_id': 3,
           'start_date': '2026-01-01'}

@pytest.fixture
def service():
    mock = AsyncMock()
    app.dependency_overrides[get_batch_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_batch_service, None)

@pytest.fixture
def batch():
    return BatchResponse(id=1, batch_name='Morning Class', course_id=2,
                         trainer_id=3, start_date=date(2026, 1, 1),
                         end_date=date(2026, 2, 1), status='Not Completed', is_active=True)


def listing(batch):
    return BatchListResponse(items=[batch], total=1, page=1, size=10)


async def test_create_success(client, service, batch):
    service.create_batch.return_value = batch
    r = await client.post(ROOT + '/', json=PAYLOAD)
    assert r.status_code == 201 and r.json()['id'] == batch.id
    service.create_batch.assert_awaited_once()


async def test_create_invalid_payload(client, service):
    r = await client.post(ROOT + '/', json={**PAYLOAD, 'invalid_field': 'value'})
    assert r.status_code == 422
    service.create_batch.assert_not_awaited()


async def test_list_success_and_filters(client, service, batch):
    service.list_batches.return_value = listing(batch)
    r = await client.get(ROOT + '/?page=2&size=5&status=Completed&is_active=false')
    assert r.status_code == 200 and r.json()['total'] == 1
    service.list_batches.assert_awaited_once()
    assert service.list_batches.await_args.kwargs['page'] == 2
    assert service.list_batches.await_args.kwargs['is_active'] is False


async def test_list_invalid_pagination(client, service):
    assert (await client.get(ROOT + '/?size=101')).status_code == 422
    service.list_batches.assert_not_awaited()


async def test_get_by_course_success(client, service, batch):
    service.get_batches_by_course.return_value = listing(batch)
    r = await client.get(ROOT + '/course/2')
    assert r.status_code == 200 and r.json()['items'][0]['course_id'] == 2
    service.get_batches_by_course.assert_awaited_once_with(2)


async def test_get_by_course_missing(client, service):
    service.get_batches_by_course.side_effect = NotFoundException('Course not found')
    assert (await client.get(ROOT + '/course/999999')).status_code == 404


async def test_get_by_trainer_success(client, service, batch):
    service.get_batches_by_trainer.return_value = listing(batch)
    r = await client.get(ROOT + '/trainer/3')
    assert r.status_code == 200 and r.json()['total'] == 1
    service.get_batches_by_trainer.assert_awaited_once_with(3)


async def test_get_by_trainer_missing(client, service):
    service.get_batches_by_trainer.side_effect = NotFoundException('Trainer not found')
    assert (await client.get(ROOT + '/trainer/999999')).status_code == 404


async def test_get_by_id_success(client, service, batch):
    service.get_batch.return_value = batch
    assert (await client.get(ROOT + '/1')).json()['id'] == 1
    service.get_batch.assert_awaited_once_with(1)


async def test_get_by_id_missing(client, service):
    service.get_batch.side_effect = NotFoundException('Batch not found')
    assert (await client.get(ROOT + '/999999')).status_code == 404


async def test_update_success(client, service, batch):
    service.update_batch.return_value = batch
    r = await client.put(ROOT + '/1', json={'batch_name': 'Updated Batch'})
    assert r.status_code == 200
    service.update_batch.assert_awaited_once()


async def test_update_invalid_payload(client, service):
    r = await client.put(ROOT + '/1', json={'start_date': '2026-03-01', 'end_date': '2026-02-01'})
    assert r.status_code == 422
    service.update_batch.assert_not_awaited()


async def test_update_status_success(client, service, batch):
    service.update_batch_status.return_value = batch
    r = await client.patch(ROOT + '/1/status', json={'status': 'Completed'})
    assert r.status_code == 200
    service.update_batch_status.assert_awaited_once()


async def test_update_status_invalid(client, service):
    assert (await client.patch(ROOT + '/1/status', json={'status': 'invalid'})).status_code == 422
    service.update_batch_status.assert_not_awaited()


async def test_activate_success(client, service, batch):
    service.activate_batch.return_value = batch
    assert (await client.patch(ROOT + '/1/activate')).status_code == 200
    service.activate_batch.assert_awaited_once_with(1)


async def test_activate_missing(client, service):
    service.activate_batch.side_effect = NotFoundException('Batch not found')
    assert (await client.patch(ROOT + '/999999/activate')).status_code == 404


async def test_delete_success(client, service):
    assert (await client.delete(ROOT + '/1')).status_code == 204
    service.delete_batch.assert_awaited_once_with(1)


async def test_delete_missing(client, service):
    service.delete_batch.side_effect = NotFoundException('Batch not found')
    assert (await client.delete(ROOT + '/999999')).status_code == 404


@pytest.mark.parametrize('method,path,json_data', [
    ('post', '/batches/', PAYLOAD),
    ('put', '/batches/1', {'batch_name': 'Updated'}),
    ('patch', '/batches/1/status', {'status': 'Completed'}),
    ('patch', '/batches/1/activate', None),
    ('delete', '/batches/1', None),
    ('get', '/batches/trainer/1', None),
])
async def test_employee_role_forbidden(client, service, as_role, method, path, json_data):
    as_role('employee')
    r = await getattr(client, method)(path, **({'json': json_data} if json_data is not None else {}))
    assert r.status_code == 403


async def test_trainer_can_read_trainer_batches(client, service, batch, as_role):
    as_role('trainer')
    service.get_batches_by_trainer.return_value = listing(batch)
    assert (await client.get(ROOT + '/trainer/3')).status_code == 200
