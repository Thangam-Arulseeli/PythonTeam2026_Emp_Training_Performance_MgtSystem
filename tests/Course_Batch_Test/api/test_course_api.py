"""Every Course route, with positive, negative and role checks."""
from unittest.mock import AsyncMock
import pytest
from app.api.dependencies.course_dependencies import get_course_service
from app.exceptions import ConflictException, NotFoundException
from app.main import app
from app.schemas.courseSchema import CourseListResponse, CourseResponse

pytestmark = [pytest.mark.api, pytest.mark.asyncio]
ROOT = '/courses'
VALID = {'course_name': 'FastAPI', 'duration_value': 2, 'duration_unit': 'weeks'}

@pytest.fixture
def service():
    mock = AsyncMock()
    app.dependency_overrides[get_course_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_course_service, None)

@pytest.fixture
def course():
    return CourseResponse(id=3, course_name='FastAPI', duration_value=2, duration_unit='weeks')


async def test_create_success(client, service, course):
    service.create_course.return_value = course
    r = await client.post(ROOT + '/', json=VALID)
    assert r.status_code == 201 and r.json()['id'] == 3
    service.create_course.assert_awaited_once()


async def test_create_invalid(client, service):
    assert (await client.post(ROOT + '/', json={**VALID, 'duration_value': 0})).status_code == 422
    service.create_course.assert_not_awaited()


async def test_create_duplicate(client, service):
    service.create_course.side_effect = ConflictException('Course name already exists')
    assert (await client.post(ROOT + '/', json=VALID)).status_code == 409


async def test_list_success_and_search(client, service, course):
    service.list_courses.return_value = CourseListResponse(items=[course], total=1, page=2, size=5)
    r = await client.get(ROOT + '/?page=2&size=5&search=fast')
    assert r.status_code == 200 and r.json()['items'][0]['id'] == 3
    service.list_courses.assert_awaited_once_with(page=2, size=5, search='fast')


async def test_list_invalid_pagination(client, service):
    assert (await client.get(ROOT + '/?page=0')).status_code == 422
    service.list_courses.assert_not_awaited()


async def test_get_success(client, service, course):
    service.get_course.return_value = course
    r = await client.get(ROOT + '/3')
    assert r.status_code == 200 and r.json()['course_name'] == 'FastAPI'
    service.get_course.assert_awaited_once_with(3)


async def test_get_missing(client, service):
    service.get_course.side_effect = NotFoundException('Course not found')
    assert (await client.get(ROOT + '/999999')).status_code == 404


async def test_update_success(client, service, course):
    service.update_course.return_value = course
    r = await client.put(ROOT + '/3', json={'description': 'New description'})
    assert r.status_code == 200
    service.update_course.assert_awaited_once()


async def test_update_invalid(client, service):
    assert (await client.put(ROOT + '/3', json={'duration_value': 0})).status_code == 422
    service.update_course.assert_not_awaited()


async def test_update_missing(client, service):
    service.update_course.side_effect = NotFoundException('Course not found')
    assert (await client.put(ROOT + '/999999', json={'description': 'change'})).status_code == 404


async def test_delete_success(client, service):
    assert (await client.delete(ROOT + '/3')).status_code == 204
    service.delete_course.assert_awaited_once_with(3)


async def test_delete_with_batches(client, service):
    service.delete_course.side_effect = ConflictException('Course has batches')
    assert (await client.delete(ROOT + '/3')).status_code == 409


@pytest.mark.parametrize('method,path,data', [
    ('post', '/courses/', VALID),
    ('put', '/courses/3', {'description': 'new'}),
    ('delete', '/courses/3', None),
])
async def test_employee_cannot_write(client, service, as_role, method, path, data):
    as_role('employee')
    r = await getattr(client, method)(path, **({'json': data} if data is not None else {}))
    assert r.status_code == 403
