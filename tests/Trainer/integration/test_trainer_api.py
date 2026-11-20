import pytest


@pytest.mark.asyncio
async def test_create_trainer_success(client, admin_headers, trainer_data):
    response = await client.post(
        "/trainers/",
        json=trainer_data,
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["trainer_name"] == "testtrainer"
    assert response.json()["email"] == "testtrainer@gmail.com"


@pytest.mark.asyncio
async def test_get_all_trainers_success(
    client,
    admin_headers,
    trainer_record,
):
    response = await client.get(
        "/trainers/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["trainer_name"] == "Test Trainer"


@pytest.mark.asyncio
async def test_get_all_trainers_empty(
    client,
    admin_headers,
):
    response = await client.get(
        "/trainers/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_trainer_by_id_success(
    client,
    admin_headers,
    trainer_record,
):
    response = await client.get(
        f"/trainers/{trainer_record.trainer_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["trainer_id"] == trainer_record.trainer_id
    assert response.json()["trainer_name"] == "Test Trainer"
    assert response.json()["email"] == "trainer_test@gmail.com"


@pytest.mark.asyncio
async def test_get_trainer_by_id_not_found(
    client,
    admin_headers,
):
    response = await client.get(
        "/trainers/999",
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trainer not found"


@pytest.mark.asyncio
async def test_get_my_trainer_details_success(
    client,
    trainer_headers,
    trainer_record,
):
    response = await client.get(
        "/trainers/me",
        headers=trainer_headers,
    )

    assert response.status_code == 200
    assert response.json()["trainer_id"] == trainer_record.trainer_id
    assert response.json()["trainer_name"] == "Test Trainer"
    assert response.json()["email"] == "trainer_test@gmail.com"


@pytest.mark.asyncio
async def test_update_trainer_success(
    client,
    admin_headers,
    trainer_record,
):
    update_data = {
        "qualification": "bcs DA",
    }

    response = await client.patch(
        f"/trainers/{trainer_record.trainer_id}",
        json=update_data,
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["trainer_id"] == trainer_record.trainer_id
    assert response.json()["qualification"] == "bcs DA"


@pytest.mark.asyncio
async def test_deactivate_trainer_success(
    client,
    admin_headers,
    trainer_record,
):
    response = await client.patch(
        f"/trainers/{trainer_record.trainer_id}/inactive",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["trainer_id"] == trainer_record.trainer_id
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_activate_trainer_success(
    client,
    admin_headers,
    trainer_record,
):
    response = await client.patch(
        f"/trainers/{trainer_record.trainer_id}/active",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["trainer_id"] == trainer_record.trainer_id
    assert response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_create_trainer_duplicate_email(
    client,
    admin_headers,
    trainer_record,
    trainer_data,
):
    trainer_data["email"] = trainer_record.email

    response = await client.post(
        "/trainers/",
        json=trainer_data,
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.asyncio
async def test_create_trainer_duplicate_phone(
    client,
    admin_headers,
    trainer_record,
    trainer_data,
):
    trainer_data["phone_number"] = trainer_record.phone_number

    response = await client.post(
        "/trainers/",
        json=trainer_data,
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Phone number already exists"


@pytest.mark.asyncio
async def test_create_trainer_invalid_data(
    client,
    admin_headers,
    trainer_data,
):
    trainer_data["experience"] = -5

    response = await client.post(
        "/trainers/",
        json=trainer_data,
        headers=admin_headers,
    )

    assert response.status_code == 422



@pytest.mark.asyncio
async def test_get_trainers_by_specialization(
    client,
    admin_headers,
    trainer_record,
):
    response = await client.get(
        "/trainers/?specialization=Python",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["trainer_name"] == "Test Trainer"
    assert "Python" in response.json()[0]["specialization"]


@pytest.mark.asyncio
async def test_search_trainers_by_name(
    client,
    admin_headers,
    trainer_record,
):
    response = await client.get(
        "/trainers/?search_by_trainer_name=Test",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["trainer_name"] == "Test Trainer"


@pytest.mark.asyncio
async def test_get_my_trainer_details_not_found(
    client,
    trainer_headers,
):
    response = await client.get(
        "/trainers/me",
        headers=trainer_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trainer details not found"


@pytest.mark.asyncio
async def test_update_trainer_not_found(
    client,
    admin_headers,
):
    update_data = {"qualification": "PhD"}

    response = await client.patch(
        "/trainers/999",
        json=update_data,
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trainer not found"


@pytest.mark.asyncio
async def test_deactivate_trainer_not_found(
    client,
    admin_headers,
):
    response = await client.patch(
        "/trainers/999/inactive",
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trainer not found"


@pytest.mark.asyncio
async def test_activate_trainer_not_found(
    client,
    admin_headers,
):
    response = await client.patch(
        "/trainers/999/active",
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trainer not found"


@pytest.mark.asyncio
async def test_admin_endpoint_without_token(client):
    response = await client.get("/trainers/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_endpoint_with_trainer_token(
    client,
    trainer_headers,
):
    response = await client.get(
        "/trainers/",
        headers=trainer_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_trainer_endpoint_with_admin_token(
    client,
    admin_headers,
):
    response = await client.get(
        "/trainers/me",
        headers=admin_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_endpoint_with_invalid_token(client):
    invalid_headers = {
        "Authorization": "Bearer invalid_token"
    }

    response = await client.get(
        "/trainers/",
        headers=invalid_headers,
    )

    assert response.status_code == 401