from datetime import datetime,UTC,timedelta
import pytest

from fastapi import HTTPException
from types import SimpleNamespace

from app.schemas.auth_schema import RegisterRequest
from app.services import auth_service as auth_module

# register success
@pytest.mark.asyncio
async def test_register_success(auth_service,db_session):
    auth_service.user_repository.staff_email_exists.return_value=True
    auth_service.user_repository.get_by_email.return_value=None
    auth_service.user_repository.get_by_username.return_value=None

    data = RegisterRequest(
        username="ramesh",
        email="ramesh.trainer@gmail.com",
        password="ramesh1234",
        role="trainer"
    )

    await auth_service.register(db_session,data)

    auth_service.user_repository.create_user.assert_awaited_once()
    db_session.commit.assert_awaited_once()


# register with invalid role
@pytest.mark.asyncio
async def test_register_invalid_role(auth_service,db_session):
    data=SimpleNamespace(
        username ="admin",
        email ="admin@gmail.com",
        password ="admin1234",
        role="admin"
    )
    with pytest.raises(HTTPException) as err:
        await auth_service.register(db_session,data)

    assert err.value.status_code == 403
    db_session.rollback.assert_awaited_once()


# registering user whose email not found existing trainer or employee table
@pytest.mark.asyncio
async def test_register_staff_email_not_found(auth_service,db_session):
    auth_service.user_repository.staff_email_exists.return_value=False
    data=RegisterRequest(
        username="Unknown",
        email="unknown@gmail.com",
        password="unknown123",
        role="employee"
    )
    with pytest.raises(HTTPException) as err:
        await auth_service.register(db_session,data)

    assert err.value.status_code == 403


# registering duplicate email
@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service,db_session):
    auth_service.user_repository.staff_email_exists.return_value=True
    auth_service.user_repository.get_by_email.return_value = object()

    data =RegisterRequest(
        username ="ramesh",
        email ="ramesh.trainer@gmail.com",
        password="ramesh1234",
        role="trainer"
    )
    with pytest.raises(HTTPException) as err:
        await auth_service.register(db_session,data)

    assert err.value.status_code == 409


# login success
@pytest.mark.asyncio
async def test_login_success(auth_service,db_session,monkeypatch):
    user = SimpleNamespace(
        user_id=1,
        username="ramesh",
        hashed_password="hashed",
        role="trainer",
        is_active =True
    )

    auth_service.user_repository.get_by_username.return_value = user

    monkeypatch.setattr(auth_module,"verify_password",lambda p ,h :True)
    monkeypatch.setattr(auth_module,"create_access_token",lambda **kwargs :"access-token")
    monkeypatch.setattr(
        auth_module,
        "create_refresh_token",
        lambda **kwargs: ("refresh-token",datetime.now(UTC) +timedelta(days=1))
    )
    monkeypatch.setattr(auth_module,"hash_refresh_token",lambda token :"hashed-refresh")

    result = await auth_service.login(db_session,"ramesh","ramesh1234")

    assert result["access_token"] == "access-token"
    assert result["refresh_token"] == "refresh-token"
    assert result["token_type"] == "bearer"
    auth_service.refresh_token_repository.create.assert_awaited_once()
    db_session.commit.assert_awaited_once()


# login with invalid username
@pytest.mark.asyncio
async def test_login_unknown_username(auth_service,db_session):
    auth_service.user_repository.get_by_username.return_value = None
    with pytest.raises(HTTPException) as err:
        await auth_service.login(db_session,"unknown","password123")

    assert err.value.status_code == 401


# login with inactive user
@pytest.mark.asyncio
async def test_login_inactive_user(auth_service,db_session,monkeypatch):
    user = SimpleNamespace(
        user_id =1,
        username="ramesh",
        hashed_password ="hashed",
        role="trainer",
        is_active =False
    )
    auth_service.user_repository.get_by_username.return_value = user
    monkeypatch.setattr(auth_module,"verify_password",lambda p,h:True)
    with pytest.raises(HTTPException) as err:
        await auth_service.login(db_session,"ramesh","ramesh1234")

    assert err.value.status_code == 403



# refresh invalid token
@pytest.mark.asyncio
async def test_refresh_invalid_token(auth_service,db_session,monkeypatch):
    monkeypatch.setattr(
        auth_module,
        "decode_token",
        lambda token : (_ for _ in ()).throw(ValueError("Invalid token"))
    )


    with pytest.raises(HTTPException) as err:
        await auth_service.refresh_tokens(db_session,"invalid-refresh-token")

    assert err.value.status_code == 401


# logout using invalid token
@pytest.mark.asyncio
async def test_logout_invalid_token(auth_service,db_session,monkeypatch):
    monkeypatch.setattr(
        auth_module,
        "decode_token",
        lambda token:(_ for _ in ()).throw(ValueError("Invalid token"))
    )
    with pytest.raises(HTTPException) as err:
        await auth_service.logout(db_session,"invalid-token",1)

    assert err.value.status_code ==401

