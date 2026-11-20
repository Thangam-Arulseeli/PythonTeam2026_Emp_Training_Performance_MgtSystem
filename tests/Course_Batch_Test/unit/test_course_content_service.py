import io
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from fastapi import UploadFile
from app.exceptions import BadRequestException, NotFoundException, PayloadTooLargeException
from app.models.course_content import CourseContent
from app.services.implementations import course_content_service as content_module
from app.services.implementations.course_content_service import CourseContentServiceImpl

@pytest.fixture
def repos():
    return AsyncMock(), AsyncMock()

@pytest.fixture
def service(repos):
    return CourseContentServiceImpl(*repos)

@pytest.mark.asyncio
async def test_upload_valid_txt(service,repos,monkeypatch,tmp_path):
    monkeypatch.setattr(content_module,'UPLOAD_DIR',tmp_path)
    repos[1].get_by_id.return_value=object()
    async def created(course_id,filename,file_path):
        assert Path(file_path).read_bytes()==b'hello'
        return CourseContent(id=1,course_id=course_id,filename=filename,file_path=file_path)
    repos[0].create.side_effect=created
    result=await service.upload(3,UploadFile(file=io.BytesIO(b'hello'),filename='notes.txt'))
    assert result.filename=='notes.txt'
    assert Path(result.file_path).exists()

@pytest.mark.asyncio
async def test_upload_invalid_extension_and_missing_course(service,repos,tmp_path,monkeypatch):
    monkeypatch.setattr(content_module,'UPLOAD_DIR',tmp_path)
    repos[1].get_by_id.return_value=None
    with pytest.raises(NotFoundException):
        await service.upload(5,UploadFile(file=io.BytesIO(b'x'),filename='a.txt'))
    repos[1].get_by_id.return_value=object()
    with pytest.raises(BadRequestException):
        await service.upload(5,UploadFile(file=io.BytesIO(b'x'),filename='a.exe'))

@pytest.mark.asyncio
async def test_upload_too_large_cleans_up(service,repos,tmp_path,monkeypatch):
    monkeypatch.setattr(content_module,'UPLOAD_DIR',tmp_path)
    monkeypatch.setattr(content_module,'MAX_FILE_SIZE',2)
    repos[1].get_by_id.return_value=object()
    with pytest.raises(PayloadTooLargeException):
        await service.upload(5,UploadFile(file=io.BytesIO(b'abc'),filename='a.txt'))
    assert not list(tmp_path.rglob('*.txt'))

@pytest.mark.asyncio
async def test_list_and_missing_file(service,repos,tmp_path):
    repos[1].get_by_id.return_value=object()
    repos[0].get_by_course.return_value=[CourseContent(id=1,course_id=2,filename='a.txt',file_path=str(tmp_path/'a.txt'))]
    result=await service.list_for_course(2)
    assert result.total==1
    repos[0].get_by_id.return_value=repos[0].get_by_course.return_value[0]
    with pytest.raises(NotFoundException):
        await service.get_file(1)

@pytest.mark.asyncio
async def test_download_and_delete(service,repos,tmp_path):
    file=tmp_path/'a.txt'
    file.write_text('hello')
    content=CourseContent(id=1,course_id=2,filename='a.txt',file_path=str(file))
    repos[0].get_by_id.return_value=content
    assert await service.get_file(1)==(str(file),'a.txt')
    await service.delete(1)
    repos[0].delete.assert_awaited_once_with(content)
    assert not file.exists()

