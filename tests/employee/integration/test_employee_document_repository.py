import pytest
from sqlalchemy.exc import IntegrityError
from app.models.employee_document import EmployeeDocument
from app.repositories.implementations.employee_document_repository import EmployeeDocumentRepositoryImpl

pytestmark = pytest.mark.integration


def document(employee_id, kind="resume", path="/tmp/test.pdf"):
    return EmployeeDocument(employee_id=employee_id, document_type=kind, file_path=path)


@pytest.mark.asyncio
async def test_create_documents_persists(test_session, sample_employee):
    repo = EmployeeDocumentRepositoryImpl(test_session)
    items = await repo.create_documents([document(sample_employee.employee_id)])
    assert items[0].document_id is not None
    assert (await repo.get_documents_by_employee_id(sample_employee.employee_id))[0].document_type == "resume"


@pytest.mark.asyncio
async def test_create_documents_duplicate_type_rejected(test_session, sample_employee):
    repo = EmployeeDocumentRepositoryImpl(test_session)
    await repo.create_documents([document(sample_employee.employee_id)])
    with pytest.raises(IntegrityError):
        await repo.create_documents([document(sample_employee.employee_id, path="/tmp/another.pdf")])




