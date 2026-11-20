import io
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile

from app.exceptions.exceptions import EmployeeNotFoundException, InvalidEmployeeDataException
from app.services.implementations import employee_document_service as module
from app.services.implementations.employee_document_service import EmployeeDocumentServiceImpl

pytestmark = pytest.mark.unit


def upload(filename, data):
    return UploadFile(filename=filename, file=io.BytesIO(data))


def setup():
    db = AsyncMock()
    employees = AsyncMock()
    docs = AsyncMock()
    employees.get_employee_by_id.return_value = object()
    return EmployeeDocumentServiceImpl(db, employees, docs), db, employees, docs




@pytest.mark.asyncio
@pytest.mark.parametrize('name,kind,content', [
    ('a.txt', 'profile_picture', b'data'),
    ('a.jpg', 'profile_picture', b''),
    ('a.png', 'profile_picture', b'invalid'),
    ('a.pdf', 'resume', b'not a PDF'),
    ('a.docx', 'resume', b'invalid zip'),
])
async def test_save_invalid_file(name, kind, content, tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'UPLOAD_DIR', tmp_path)
    svc, _, _, _ = setup()
    with pytest.raises(InvalidEmployeeDataException):
        await svc.save_file(upload(name, content), kind)
    assert not list(tmp_path.rglob('*'))


@pytest.mark.asyncio
@pytest.mark.parametrize('kind,max_size,extension', [
    ('profile_picture', module.IMAGE_MAX_SIZE, 'png'),
    ('resume', module.RESUME_MAX_SIZE, 'pdf'),
])
async def test_large_file_rejected(kind, max_size, extension, tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'UPLOAD_DIR', tmp_path)
    svc, _, _, _ = setup()
    with pytest.raises(InvalidEmployeeDataException, match='exceeds'):
        await svc.save_file(upload('large.' + extension, b'Z' * (max_size + 1)), kind)




@pytest.mark.asyncio
async def test_upload_stores_documents(tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'UPLOAD_DIR', tmp_path)
    svc, db, _, repo = setup()
    async def create(docs):
        return docs
    repo.create_documents.side_effect = create
    result = await svc.upload_documents(100, profile_picture=upload('x.jpg', b'\xff\xd8\xffabc'),
                                         resume=upload('x.pdf', b'%PDF-1.4'))
    assert {doc.document_type for doc in result} == {'profile_picture', 'resume'}
    assert all(Path(doc.file_path).exists() for doc in result)
    db.commit.assert_awaited_once()
    assert db.refresh.await_count == 2


@pytest.mark.asyncio
async def test_upload_failure_removes_saved_files(tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'UPLOAD_DIR', tmp_path)
    svc, db, _, repo = setup()
    repo.create_documents.side_effect = RuntimeError('database unavailable')
    with pytest.raises(RuntimeError):
        await svc.upload_documents(100, resume=upload('a.pdf', b'%PDF-1.4'))
    db.rollback.assert_awaited_once()
    assert not list(tmp_path.rglob('*.pdf'))


