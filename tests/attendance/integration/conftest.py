from datetime import UTC, date, datetime, time
from types import SimpleNamespace

import pytest
import pytest_asyncio
from fastapi import HTTPException, Request
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_attendance_session_service, get_current_user
from app.exceptions import ConflictException, NotAuthorizedException, NotFoundException
from app.main import app


class StubAttendanceSessionService:
    """Keep HTTP integration tests isolated from a locally configured database."""

    def __init__(self):
        self.sessions = {
            101: self._session(101, 10, trainer_id=20),
            102: self._session(102, 30, trainer_id=21),
            103: self._session(103, 10, trainer_id=20),
        }

    @staticmethod
    def _session(session_id, batch_id, trainer_id, status="scheduled"):
        now = datetime.now(UTC)
        return SimpleNamespace(
            id=session_id,
            batch_id=batch_id,
            session_date=date(2026, 11, 20),
            start_time=time(9),
            end_time=time(10),
            topic="Python Fundamentals",
            description="Integration test session",
            status=status,
            created_at=now,
            updated_at=now,
            batch=SimpleNamespace(trainer_id=trainer_id),
        )

    async def create(self, data, user):
        if data.batch_id not in (10, 20, 30):
            raise NotFoundException(f"Batch with id {data.batch_id} not found")
        if user.role == "trainer" and data.batch_id != 20:
            raise NotAuthorizedException("Trainer is not assigned to this batch")
        session = self._session(200 + len(self.sessions), data.batch_id, 20)
        session.session_date = data.session_date
        session.start_time = data.start_time
        session.end_time = data.end_time
        session.topic = data.topic
        session.description = data.description
        session.status = data.status
        self.sessions[session.id] = session
        return session

    async def get_all_sessions(self, user, filters):
        return list(self.sessions.values())

    async def get_current_user_sessions(self, user):
        return list(self.sessions.values())

    async def get_session_by_id(self, session_id, user):
        session = self.sessions.get(session_id)
        if session is None:
            raise NotFoundException("Session not found")
        if user.role == "employee" and session.batch_id != 10:
            raise NotAuthorizedException("Employee is not enrolled in this batch")
        if user.role == "trainer" and session.batch.trainer_id != 20:
            raise NotAuthorizedException("Trainer is not assigned to this batch")
        return session

    async def update_session(self, session_id, data, user):
        session = await self.get_session_by_id(session_id, user)
        fields = data.model_dump(exclude_unset=True)
        if fields.get("status") == "completed" and session.status != "completed":
            raise ConflictException("Use the complete-session endpoint")
        for name, value in fields.items():
            setattr(session, name, value)
        return session

    async def get_by_trainer_id(self, trainer_id):
        return [
            session
            for session in self.sessions.values()
            if session.batch.trainer_id == trainer_id
        ]

    async def get_session_summary(self, session_id, user):
        await self.get_session_by_id(session_id, user)
        return {
            "present": 0,
            "absent": 0,
            "unmarked": 0,
            "attendance_percentage": 0,
            "is_finalized": False,
        }

    async def complete_session(self, session_id, user):
        session = await self.get_session_by_id(session_id, user)
        session.status = "completed"
        return session


@pytest_asyncio.fixture
async def client():
    service = StubAttendanceSessionService()

    async def get_test_user(request: Request):
        authorization = request.headers.get("Authorization")
        roles = {
            "Bearer test-admin-token": (1, "admin", "admin@example.com"),
            "Bearer test-trainer-token": (2, "trainer", "trainer@example.com"),
            "Bearer test-employee-token": (3, "employee", "employee@example.com"),
        }
        identity = roles.get(authorization)
        if identity is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user_id, role, email = identity
        return SimpleNamespace(user_id=user_id, role=role, email=email)

    app.dependency_overrides[get_current_user] = get_test_user
    app.dependency_overrides[get_attendance_session_service] = lambda: service
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers():
    return {"Authorization": "Bearer test-admin-token"}


@pytest.fixture
def trainer_headers():
    return {"Authorization": "Bearer test-trainer-token"}


@pytest.fixture
def employee_headers():
    return {"Authorization": "Bearer test-employee-token"}


@pytest.fixture
def attendance_test_data():
    return {
        "batch_id": 10,
        "trainer_batch_id": 20,
        "other_batch_id": 30,
        "session_id": 101,
        "other_session_id": 102,
        "session_to_complete_id": 103,
        "trainer_id": 20,
    }
