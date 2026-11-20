from pathlib import Path

import pytest
from httpx import AsyncClient

from app.models import EmployeeData
from app.services.implementations import employee_document_service as document_module

pytestmark = pytest.mark.api
BASE = "/api/employees"


@pytest.mark.asyncio
async def test_upload_resume_success(
    client: AsyncClient,
    sample_employee: EmployeeData,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(document_module, "UPLOAD_DIR", tmp_path)
    r = await client.post(f"{BASE}/{sample_employee.employee_id}/documents", files={"resume": ("cv.pdf", b"%PDF-1.4\nOK", "application/pdf")})
    assert r.status_code == 201, r.text
    assert r.json()[0]["document_type"] == "resume"
    assert list(tmp_path.rglob("*.pdf"))




@pytest.mark.asyncio
async def test_upload_invalid_format_rejected(
    client: AsyncClient,
    sample_employee: EmployeeData,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(document_module, "UPLOAD_DIR", tmp_path)
    r = await client.post(f"{BASE}/{sample_employee.employee_id}/documents", files={"resume": ("bad.txt", b"TEXT", "text/plain")})
    assert r.status_code == 422
    assert not list(tmp_path.rglob("*.txt"))




@pytest.mark.asyncio
async def test_get_documents_success(
    client: AsyncClient,
    sample_employee: EmployeeData,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(document_module, "UPLOAD_DIR", tmp_path)
    r = await client.post(f"{BASE}/{sample_employee.employee_id}/documents", files={"resume": ("cv.pdf", b"%PDF-1.4\nOK", "application/pdf")})
    assert r.status_code == 201, r.text
    listed = await client.get(f"{BASE}/{sample_employee.employee_id}/documents")
    assert listed.status_code == 200, listed.text
    assert len(listed.json()["documents"]) == 1


@pytest.mark.asyncio
async def test_get_documents_missing_employee_rejected(client: AsyncClient) -> None:
    assert (await client.get(BASE + "/999999999/documents")).status_code == 404
