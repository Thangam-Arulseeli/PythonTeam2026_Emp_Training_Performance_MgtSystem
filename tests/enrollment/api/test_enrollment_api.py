
import pytest

@pytest.mark.asyncio
async def test_create_enrollment(client,employee,batch):
    response = await client.post(
        "/api/enrollments/",
        json={
            "employee_id": employee.employee_id,
            "batch_id": batch.id,
        },
    )
    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "Enrolled"
    assert data["employee"]["full_name"] == "Test Employee"
    assert data["batch"]["batch_name"] == "Python Batch 01"
    assert data["batch"]["course"]["course_name"] == "Python Testing"


@pytest.mark.asyncio
async def test_create_enrollment_invalid_employee(client,batch):
    response = await client.post(
        "/api/enrollments/",
        json={
            "employee_id": 99999,
            "batch_id": batch.id,
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_enrollment_duplicate(
    client,
    employee,
    batch,
    enrollment,
):
    response = await client.post(
        "/api/enrollments/",
        json={
            "employee_id": employee.employee_id,
            "batch_id": batch.id,
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_enrollment_invalid_input(client,batch):
    response = await client.post(
        "/api/enrollments/",
        json={
            "employee_id": -1,
            "batch_id": batch.id,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_enrollment_inactive_employee(
    client,
    db_session,
    employee,
    batch,
):
    employee.is_active = False
    await db_session.commit()

    response = await client.post(
        "/api/enrollments/",
        json={
            "employee_id": employee.employee_id,
            "batch_id": batch.id,
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_enrollment_inactive_batch(
    client,
    db_session,
    employee,
    batch,
):
    batch.is_active = False
    await db_session.commit()

    response = await client.post(
        "/api/enrollments/",
        json={
            "employee_id": employee.employee_id,
            "batch_id": batch.id,
        },
    )
    assert response.status_code == 422


# get enrollment by id

@pytest.mark.asyncio
async def test_get_enrollment(client,enrollment):
    response = await client.get(
        f"/api/enrollments/{enrollment.enrollment_id}"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Enrolled"


@pytest.mark.asyncio
async def test_get_enrollment_not_found(client):
    response = await client.get("/api/enrollments/99999")

    assert response.status_code == 404


# get all enrollments

@pytest.mark.asyncio
async def test_get_all_enrollments(client,enrollment):
    response = await client.get("/api/enrollments/")
    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_get_enrollments_with_status_filter(client,enrollment):
    response = await client.get(
        "/api/enrollments/?status=Enrolled"
    )
    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["status"] == "Enrolled"


@pytest.mark.asyncio
async def test_get_enrollments_with_pagination(client, enrollment):
    response = await client.get("/api/enrollments/?page=1&size=5")
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["size"] == 5
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_enrollments_invalid_page(client):
    response = await client.get("/api/enrollments/?page=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_enrollments_invalid_size(client):
    response = await client.get("/api/enrollments/?size=101")
    assert response.status_code == 422


# get enrollments by batch

@pytest.mark.asyncio
async def test_get_enrollments_by_batch(
    client,
    enrollment,
    batch,
):
    response = await client.get(
        f"/api/enrollments/batch/{batch.id}"
    )
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["batch"]["batch_name"] == "Python Batch 01"


@pytest.mark.asyncio
async def test_get_enrollments_by_invalid_batch(client):
    response = await client.get("/api/enrollments/batch/99999")
    assert response.status_code == 404


# get enrollments by employee id

@pytest.mark.asyncio
async def test_get_enrollments_by_employee(
    client,
    enrollment,
    employee,
):
    response = await client.get(
        f"/api/enrollments/employee/{employee.employee_id}"
    )
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["employee"]["full_name"] == "Test Employee"


@pytest.mark.asyncio
async def test_get_enrollments_by_employee_without_enrollment(client,employee):
    response = await client.get(
        f"/api/enrollments/employee/{employee.employee_id}"
    )
    assert response.status_code == 200
    assert response.json() == []



# update enrollment status

@pytest.mark.asyncio
async def test_pause_enrollment(
    client,
    enrollment,
):
    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Paused",
            "remarks": "Employee requested a temporary break",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Paused"


@pytest.mark.asyncio
async def test_resume_enrollment(
    client,
    db_session,
    enrollment,
):

    enrollment.status = "Paused"
    enrollment.remarks = "Temporary break"
    await db_session.commit()

    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Enrolled",
            "remarks": "Employee resumed training",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Enrolled"


@pytest.mark.asyncio
async def test_cancel_enrollment(client, enrollment):
    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Cancelled",
            "remarks": "Employee withdrew from training",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Cancelled"


@pytest.mark.asyncio
async def test_complete_enrollment(
    client,
    db_session,
    enrollment,
    batch,
):
    batch.status = "completed"
    await db_session.commit()

    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Completed",
            "remarks": "Successfully completed training",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Completed"


@pytest.mark.asyncio
async def test_pause_without_remarks(client, enrollment):
    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Paused",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_cancel_without_remarks(client, enrollment):
    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Cancelled",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_complete_before_batch_completion(client,enrollment):
    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Completed",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_same_status(client, enrollment):
    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Enrolled",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_invalid_status(client,enrollment):
    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Pending",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_nonexistent_enrollment(client):
    response = await client.patch(
        "/api/enrollments/99999/status",
        json={
            "status": "Paused",
            "remarks": "Testing",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_cancelled_enrollment(
    client,
    db_session,
    enrollment
):
    enrollment.status = "Cancelled"
    enrollment.remarks = "Already cancelled"
    await db_session.commit()

    response = await client.patch(
        f"/api/enrollments/{enrollment.enrollment_id}/status",
        json={
            "status": "Enrolled",
        },
    )
    assert response.status_code == 409
