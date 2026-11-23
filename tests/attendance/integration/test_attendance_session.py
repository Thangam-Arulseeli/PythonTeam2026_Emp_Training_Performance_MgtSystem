from datetime import date, timedelta

import pytest

BASE_URL = "/api/attendance/session"


def session_payload(batch_id):
    return {
        "batch_id": batch_id,
        "session_date": (date.today() + timedelta(days=1)).isoformat(),
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "topic": "Python Fundamentals",
        "description": "Integration test session",
        "status": "scheduled",
    }


@pytest.mark.asyncio
async def test_admin_can_create_session(client, admin_headers, attendance_test_data):
    response = await client.post(
        f"{BASE_URL}/create",
        json=session_payload(attendance_test_data["batch_id"]),
        headers=admin_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["batch_id"] == attendance_test_data["batch_id"]
    assert data["status"] == "scheduled"
    assert "id" in data


@pytest.mark.asyncio
async def test_trainer_can_create_session_for_assigned_batch(
    client, trainer_headers, attendance_test_data
):
    response = await client.post(
        f"{BASE_URL}/create",
        json=session_payload(attendance_test_data["trainer_batch_id"]),
        headers=trainer_headers,
    )

    assert response.status_code == 201
    assert response.json()["batch_id"] == attendance_test_data["trainer_batch_id"]


@pytest.mark.asyncio
async def test_trainer_cannot_create_session_for_unassigned_batch(
    client, trainer_headers, attendance_test_data
):
    response = await client.post(
        f"{BASE_URL}/create",
        json=session_payload(attendance_test_data["other_batch_id"]),
        headers=trainer_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_employee_cannot_create_session(
    client, employee_headers, attendance_test_data
):
    response = await client.post(
        f"{BASE_URL}/create",
        json=session_payload(attendance_test_data["batch_id"]),
        headers=employee_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_session_with_invalid_batch(client, admin_headers):
    response = await client.post(
        f"{BASE_URL}/create",
        json=session_payload(999999),
        headers=admin_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_session_with_invalid_time(
    client, admin_headers, attendance_test_data
):
    payload = session_payload(attendance_test_data["batch_id"])
    payload["start_time"] = "11:00:00"
    payload["end_time"] = "10:00:00"

    response = await client.post(
        f"{BASE_URL}/create",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_all_sessions_as_admin(client, admin_headers):
    response = await client.get(
        BASE_URL + "/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_all_sessions_as_trainer(client, trainer_headers):
    response = await client.get(
        BASE_URL + "/",
        headers=trainer_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_all_sessions_as_employee(client, employee_headers):
    response = await client.get(
        BASE_URL + "/",
        headers=employee_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_session_by_id(client, admin_headers, attendance_test_data):
    response = await client.get(
        f"{BASE_URL}/{attendance_test_data['session_id']}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == attendance_test_data["session_id"]


@pytest.mark.asyncio
async def test_get_nonexistent_session(client, admin_headers):
    response = await client.get(
        f"{BASE_URL}/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_employee_cannot_access_unenrolled_session(
    client, employee_headers, attendance_test_data
):
    response = await client.get(
        f"{BASE_URL}/{attendance_test_data['other_session_id']}",
        headers=employee_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_trainer_cannot_access_another_trainers_session(
    client, trainer_headers, attendance_test_data
):
    response = await client.get(
        f"{BASE_URL}/{attendance_test_data['other_session_id']}",
        headers=trainer_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_session(client, admin_headers, attendance_test_data):
    response = await client.patch(
        f"{BASE_URL}/{attendance_test_data['session_id']}/update-session",
        json={"topic": "Advanced Python"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == attendance_test_data["session_id"]


@pytest.mark.asyncio
async def test_update_nonexistent_session(client, admin_headers):
    response = await client.patch(
        f"{BASE_URL}/999999/update-session",
        json={"topic": "Updated topic"},
        headers=admin_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_employee_cannot_update_session(
    client, employee_headers, attendance_test_data
):
    response = await client.patch(
        f"{BASE_URL}/{attendance_test_data['session_id']}/update-session",
        json={"topic": "Unauthorized update"},
        headers=employee_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_trainer_cannot_update_another_trainers_session(
    client, trainer_headers, attendance_test_data
):
    response = await client.patch(
        f"{BASE_URL}/{attendance_test_data['other_session_id']}/update-session",
        json={"topic": "Unauthorized update"},
        headers=trainer_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_cannot_complete_session_through_update_endpoint(
    client, admin_headers, attendance_test_data
):
    response = await client.patch(
        f"{BASE_URL}/{attendance_test_data['session_id']}/update-session",
        json={"status": "completed"},
        headers=admin_headers,
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_my_sessions_as_trainer(client, trainer_headers):
    response = await client.get(
        f"{BASE_URL}/my-sessions",
        headers=trainer_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_my_sessions_as_employee(client, employee_headers):
    response = await client.get(
        f"{BASE_URL}/my-sessions",
        headers=employee_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_admin_can_get_sessions_by_trainer(
    client, admin_headers, attendance_test_data
):
    response = await client.get(
        f"{BASE_URL}/{attendance_test_data['trainer_id']}/trainer",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_employee_cannot_get_sessions_by_trainer(
    client, employee_headers, attendance_test_data
):
    response = await client.get(
        f"{BASE_URL}/{attendance_test_data['trainer_id']}/trainer",
        headers=employee_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_session_summary(client, trainer_headers, attendance_test_data):
    response = await client.get(
        f"{BASE_URL}/{attendance_test_data['session_id']}/summary",
        headers=trainer_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "present" in data
    assert "absent" in data
    assert "unmarked" in data
    assert "attendance_percentage" in data
    assert "is_finalized" in data


@pytest.mark.asyncio
async def test_employee_cannot_get_session_summary(
    client, employee_headers, attendance_test_data
):
    response = await client.get(
        f"{BASE_URL}/{attendance_test_data['session_id']}/summary",
        headers=employee_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_complete_session(client, trainer_headers, attendance_test_data):
    response = await client.patch(
        f"{BASE_URL}/{attendance_test_data['session_to_complete_id']}/complete",
        headers=trainer_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_complete_nonexistent_session(client, admin_headers):
    response = await client.patch(
        f"{BASE_URL}/999999/complete",
        headers=admin_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_employee_cannot_complete_session(
    client, employee_headers, attendance_test_data
):
    response = await client.patch(
        f"{BASE_URL}/{attendance_test_data['session_id']}/complete",
        headers=employee_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_user_cannot_access_sessions(client):
    response = await client.get(f"{BASE_URL}/")

    assert response.status_code in (401, 403)
