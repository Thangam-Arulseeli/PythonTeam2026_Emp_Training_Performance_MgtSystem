"""Every Course Content route: upload, list, download and delete."""
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from app.api.dependencies.course_content_dependencies import get_course_content_service
from app.exceptions import BadRequestException, NotFoundException, PayloadTooLargeException
from app.main import app
from app.schemas.course_content_schema import CourseContentListResponse, CourseContentResponse

pytestmark = [pytest.mark.api, pytest.mark.asyncio]

@pytest.fixture
def service():
    mock = AsyncMock()
    app.dependency_overrides[get_course_content_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_course_content_service, None)

@pytest.fixture
def content(tmp_path):
    return CourseContentResponse(id=2, course_id=1, filename='lesson.txt', file_path=str(tmp_path / 'lesson.txt'))


async def test_upload_success(client, service, content):
    service.upload.return_value = content
    r = await client.post('/courses/1/contents', files={'file': ('lesson.txt', b'hello', 'text/plain')})
    assert r.status_code == 201 and r.json()['filename'] == 'lesson.txt'
    service.upload.assert_awaited_once()


async def test_upload_missing_file(client, service):
    assert (await client.post('/courses/1/contents')).status_code == 422
    service.upload.assert_not_awaited()


async def test_upload_unsupported_type(client, service):
    service.upload.side_effect = BadRequestException('Unsupported file type')
    r = await client.post('/courses/1/contents', files={'file': ('bad.exe', b'x')})
    assert r.status_code == 400


async def test_upload_missing_course(client, service):
    service.upload.side_effect = NotFoundException('Course not found')
    r = await client.post('/courses/999999/contents', files={'file': ('a.txt', b'x')})
    assert r.status_code == 404


async def test_upload_too_large(client, service):
    service.upload.side_effect = PayloadTooLargeException('File too large')
    r = await client.post('/courses/1/contents', files={'file': ('a.pdf', b'fake')})
    assert r.status_code == 413


async def test_list_success(client, service, content):
    service.list_for_course.return_value = CourseContentListResponse(items=[content], total=1, page=1, size=1)
    r = await client.get('/courses/1/contents')
    assert r.status_code == 200 and r.json()['total'] == 1
    service.list_for_course.assert_awaited_once_with(course_id=1)


async def test_list_missing_course(client, service):
    service.list_for_course.side_effect = NotFoundException('Course not found')
    assert (await client.get('/courses/999999/contents')).status_code == 404


async def test_download_success(client, service, content):
    Path(content.file_path).write_bytes(b'lesson body')
    service.get_file.return_value = (content.file_path, content.filename)
    r = await client.get('/courses/contents/2/download')
    assert r.status_code == 200 and r.content == b'lesson body'
    service.get_file.assert_awaited_once_with(content_id=2)


async def test_download_missing(client, service):
    service.get_file.side_effect = NotFoundException('Content not found')
    assert (await client.get('/courses/contents/999999/download')).status_code == 404


async def test_delete_success(client, service):
    assert (await client.delete('/courses/contents/2')).status_code == 204
    service.delete.assert_awaited_once_with(content_id=2)


async def test_delete_missing(client, service):
    service.delete.side_effect = NotFoundException('Content not found')
    assert (await client.delete('/courses/contents/999999')).status_code == 404


@pytest.mark.parametrize('method,path,files', [
    ('post', '/courses/1/contents', {'file': ('a.txt', b'hello')}),
    ('delete', '/courses/contents/2', None),
])
async def test_employee_cannot_modify_content(client, service, as_role, method, path, files):
    as_role('employee')
    r = await getattr(client, method)(path, **({'files': files} if files is not None else {}))
    assert r.status_code == 403


async def test_trainer_can_upload(client, service, content, as_role):
    as_role('trainer')
    service.upload.return_value = content
    r = await client.post('/courses/1/contents', files={'file': ('lesson.txt', b'hello')})
    assert r.status_code == 201
