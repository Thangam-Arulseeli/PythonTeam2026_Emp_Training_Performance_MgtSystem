import pytest
from pydantic import ValidationError
from unittest.mock import AsyncMock
from app.exceptions import ConflictException, NotFoundException
from app.models.course import Course
from app.schemas.courseSchema import CourseCreate, CourseUpdate
from app.services.implementations.course_service import CourseServiceImpl


def course_model(id=1, name='Python'):
    return Course(id=id, course_name=name, description='Overview', duration_value=2, duration_unit='weeks')

@pytest.fixture
def repo():
    return AsyncMock()

@pytest.fixture
def service(repo):
    return CourseServiceImpl(repo)

@pytest.mark.asyncio
async def test_create_course(service, repo):
    repo.get_by_name.return_value = None
    repo.create.return_value = course_model()
    value = await service.create_course(CourseCreate(course_name='Python', duration_value=2, duration_unit='weeks'))
    assert value.course_name == 'Python'
    assert repo.create.await_args.args[0]['duration_unit'] == 'weeks'

@pytest.mark.asyncio
async def test_create_duplicate(service, repo):
    repo.get_by_name.return_value = course_model()
    with pytest.raises(ConflictException):
        await service.create_course(CourseCreate(course_name='Python', duration_value=1, duration_unit='days'))
    repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_pagination(service, repo):
    repo.get_all.return_value = ([course_model()], 15)
    result = await service.list_courses(page=2, size=5, search='py')
    repo.get_all.assert_awaited_once_with(5, 5, 'py')
    assert result.total == 15 and len(result.items) == 1

@pytest.mark.asyncio
async def test_update_and_duplicate_name(service, repo):
    original = course_model()
    repo.get_by_id.return_value = original
    repo.get_by_name.return_value = None
    repo.update.return_value = course_model(name='Updated')
    result = await service.update_course(1, CourseUpdate(course_name='Updated'))
    assert result.course_name == 'Updated'
    repo.update.assert_awaited_once()
    repo.get_by_name.return_value = course_model(2, 'Other')
    with pytest.raises(ConflictException):
        await service.update_course(1, CourseUpdate(course_name='Other'))

@pytest.mark.asyncio
async def test_update_duration_too_large(service, repo):
    with pytest.raises(ValidationError, match="Duration exceeds the maximum supported length"):
        CourseUpdate(duration_value=100, duration_unit='years')

@pytest.mark.asyncio
async def test_delete_rejects_batches(service, repo):
    repo.get_by_id.return_value = course_model()
    repo.has_batches.return_value = True
    with pytest.raises(ConflictException):
        await service.delete_course(1)
    repo.delete.assert_not_awaited()

@pytest.mark.asyncio
async def test_delete_without_batches(service, repo):
    repo.get_by_id.return_value = course_model()
    repo.has_batches.return_value = False
    repo.get_content_file_paths.return_value = []
    await service.delete_course(1)
    repo.delete.assert_awaited_once()
