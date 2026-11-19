import pytest
from app.repositories.implementations.course_content_repository import CourseContentRepository

@pytest.mark.asyncio
async def test_content_create_read_list_delete(test_session,sample_course,tmp_path):
    repo=CourseContentRepository(test_session)
    path=tmp_path/'lesson.txt'
    path.write_text('test file')
    content=await repo.create(sample_course.id,'lesson.txt',str(path))
    assert content.id is not None
    assert (await repo.get_by_id(content.id)).filename=='lesson.txt'
    found=await repo.get_by_course(sample_course.id)
    assert any(item.id==content.id for item in found)
    await repo.delete(content)
    assert await repo.get_by_id(content.id) is None

@pytest.mark.asyncio
async def test_missing_course_content(test_session):
    repo=CourseContentRepository(test_session)
    assert await repo.get_by_id(-1) is None
    assert await repo.get_by_course(-1)==[]
