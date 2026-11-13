from datetime import datetime,UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.service_dependencies import get_auth_service
from app.database.session import get_session
from app.main import app
from app.services.auth_service import AuthService

@pytest.fixture
def db_session():
    return AsyncMock()


@pytest.fixture
def auth_service():
    return AuthService(
        user_repository=AsyncMock(),
        refresh_token_repository=AsyncMock()
    )


@pytest.fixture
def fakeuser():
    return SimpleNamespace(
        user_id =1,
        username ="ramesh",
        email="ramesh.trainer@gmail.com",
        hashed_password ="hashed_password",
        role="trainer",
        is_active=True,
        created_at = datetime.now(UTC)
    )

@pytest.fixture
def api_service():
    return AsyncMock(spec=AuthService)


@pytest.fixture
def client(api_service, fakeuser):
    app.dependency_overrides[get_auth_service] =lambda: api_service
    app.dependency_overrides[get_session] = lambda: AsyncMock()
    app.dependency_overrides[get_current_user] =lambda: fakeuser

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client(api_service):
    app.dependency_overrides[get_auth_service]=api_service
    app.dependency_overrides[get_session]=lambda:AsyncMock
    app.dependency_overrides.pop(get_current_user,None)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

