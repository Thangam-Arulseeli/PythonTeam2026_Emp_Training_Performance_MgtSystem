import pytest

pytestmark = pytest.mark.api
BASE = "/api/employees"


@pytest.mark.asyncio
async def test_create_success(client, sample_employee_data):
    r = await client.post(BASE + "/", json=sample_employee_data)
    assert r.status_code == 201, r.text
    assert r.json()["email"] == sample_employee_data["email"]
    assert r.json()["role"] == "employee"


@pytest.mark.asyncio
async def test_create_duplicate_rejected(client, sample_employee_data):
    assert (await client.post(BASE + "/", json=sample_employee_data)).status_code == 201
    r = await client.post(BASE + "/", json=sample_employee_data)
    assert r.status_code == 409, r.text


@pytest.mark.asyncio
async def test_list_active_success(client, sample_employee):
    r = await client.get(BASE + "/", params={"skip": 0, "limit": 10})
    assert r.status_code == 200
    assert sample_employee.employee_id in [x["employee_id"] for x in r.json()]




@pytest.mark.asyncio
async def test_list_inactive_success(client, sample_employee):
    assert (await client.delete(f"{BASE}/{sample_employee.employee_id}")).status_code == 200
    r = await client.get(BASE + "/inactive_employee")
    assert r.status_code == 200
    assert sample_employee.employee_id in [x["employee_id"] for x in r.json()]




@pytest.mark.asyncio
async def test_get_employee_success(client, sample_employee):
    r = await client.get(f"{BASE}/{sample_employee.employee_id}")
    assert r.status_code == 200
    assert r.json()["employee_id"] == sample_employee.employee_id


@pytest.mark.asyncio
async def test_get_employee_missing(client):
    assert (await client.get(BASE + "/999999999")).status_code == 404


@pytest.mark.asyncio
async def test_patch_employee_success(client, sample_employee):
    r = await client.patch(f"{BASE}/{sample_employee.employee_id}", json={"full_name": "Updated Name"})
    assert r.status_code == 200, r.text
    assert r.json()["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_patch_employee_invalid(client, sample_employee):
    r = await client.patch(f"{BASE}/{sample_employee.employee_id}", json={"role": "admin"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_delete_employee_success(client, sample_employee):
    r = await client.delete(f"{BASE}/{sample_employee.employee_id}")
    assert r.status_code == 200, r.text
    assert r.json()["employee_id"] == sample_employee.employee_id
    assert (await client.get(f"{BASE}/{sample_employee.employee_id}")).status_code == 404




@pytest.mark.asyncio
async def test_reactivate_employee_success(client, sample_employee):
    eid = sample_employee.employee_id
    assert (await client.delete(f"{BASE}/{eid}")).status_code == 200
    r = await client.put(f"{BASE}/{eid}/reactivate")
    assert r.status_code == 200, r.text
    assert r.json()["is_active"] is True


