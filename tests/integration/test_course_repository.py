import pytest
from uuid import uuid4
from app.repositories.implementations.course_repository import CourseRepository

@pytest.mark.asyncio
async def test_create_read_list_search_update_delete(test_session):
    repo = CourseRepository(test_session)
    name = 'Integration ' + uuid4().hex[:12]
    course = await repo.create({'course_name': name, 'duration_value': 3, 'duration_unit': 'days', 'description': 'FastAPI testing'})
    assert course.id is not None
    assert (await repo.get_by_id(course.id)).course_name == name
    assert (await repo.get_by_name('  ' + name.upper() + ' ')).id == course.id
    items, count = await repo.get_all(0, 10, 'FastAPI testing')
    assert count >= 1 and any(item.id == course.id for item in items)
    updated = await repo.update(course, {'duration_value': 5})
    assert updated.duration_value == 5
    assert await repo.has_batches(course.id) is False
    assert await repo.get_content_file_paths(course.id) == []
    await repo.delete(course)
    assert await repo.get_by_id(course.id) is None

@pytest.mark.asyncio
async def test_missing_course(test_session):
    repo = CourseRepository(test_session)
    assert await repo.get_by_id(-1) is None
    assert await repo.get_by_name('not-existing-' + uuid4().hex) is None
