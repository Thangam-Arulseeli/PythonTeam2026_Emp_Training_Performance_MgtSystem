import pytest

from app.models.trainer_resume import TrainerResume


@pytest.mark.asyncio
async def test_get_trainer_resume_success(
    client,
    admin_headers,
    trainer_record,
    test_session,
):
    resume = TrainerResume(
        trainer_id=trainer_record.trainer_id,
        file_name="trainer_resume.pdf",
        file_path="uploads/trainer_resumes/trainer_resume.pdf",
    )

    test_session.add(resume)
    await test_session.commit()
    await test_session.refresh(resume)

    response = await client.get(
        f"/trainers/{trainer_record.trainer_id}/resume",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["resume_id"] == resume.resume_id
    assert response.json()["trainer_id"] == trainer_record.trainer_id
    assert response.json()["file_name"] == "trainer_resume.pdf"


@pytest.mark.asyncio
async def test_upload_trainer_resume_success(
    client,
    admin_headers,
    trainer_record,
):
    file_content = b"sample PDF resume."

    response = await client.post(
        f"/trainers/{trainer_record.trainer_id}/resume",
        files={
            "file": (
                "trainer_resume.pdf",
                file_content,
                "application/pdf",
            )
        },
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["trainer_id"] == trainer_record.trainer_id
    assert response.json()["file_name"] == "trainer_resume.pdf"


@pytest.mark.asyncio
async def test_get_trainer_resume_trainer_not_found(
    client,
    admin_headers,
):
    response = await client.get(
        "/trainers/999/resume",
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trainer not found"

@pytest.mark.asyncio
async def test_get_trainer_resume_not_found(
    client,
    admin_headers,
    trainer_record,
):
    response = await client.get(
        f"/trainers/{trainer_record.trainer_id}/resume",
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"


@pytest.mark.asyncio
async def test_upload_trainer_resume_trainer_not_found(
    client,
    admin_headers,
):
    file_content = b"sample PDF resume."

    response = await client.post(
        "/trainers/999/resume",
        files={
            "file": (
                "trainer_resume.pdf",
                file_content,
                "application/pdf",
            )
        },
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trainer not found"



@pytest.mark.asyncio
async def test_upload_trainer_resume_invalid_file_type(
    client,
    admin_headers,
    trainer_record,
):
    file_content = b"sample text file."

    response = await client.post(
        f"/trainers/{trainer_record.trainer_id}/resume",
        files={
            "file": (
                "trainer_resume.txt",
                file_content,
                "text/plain",
            )
        },
        headers=admin_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed"


@pytest.mark.asyncio
async def test_upload_trainer_resume_missing_file(
    client,
    admin_headers,
    trainer_record,
):
    response = await client.post(
        f"/trainers/{trainer_record.trainer_id}/resume",
        headers=admin_headers,
    )

    assert response.status_code == 422