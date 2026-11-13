from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.service_dependencies import get_auth_service
from app.database.session import get_session
from app.models.user import User
from app.schemas.auth_schema import (
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

AuthServiceDependency = Annotated[AuthService,Depends(get_auth_service)]

# register
@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest,
    service: AuthServiceDependency,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    await service.register(db, data)
    return MessageResponse(
        message="Registration successful. You can now log in."
    )


# login
@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    data: Annotated[OAuth2PasswordRequestForm,Depends()],
    service: AuthServiceDependency,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    return await service.login(db,data.username, data.password)


# refresh
@router.post(
    "/refresh",
    response_model=TokenResponse
)
async def refresh(
    data: RefreshRequest,
    service: AuthServiceDependency,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    return await service.refresh_tokens(
        db,data.refresh_token
    )


# logout
@router.post(
    "/logout",
    response_model=MessageResponse
)
async def logout(
    data: RefreshRequest,
    service: AuthServiceDependency,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(get_current_user)
):
    await service.logout(
        db,data.refresh_token,current_user.user_id
    )

    return MessageResponse(
        message="Logged out successfully."
    )


# current user
@router.get(
    "/me",
    response_model=UserProfileResponse
)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
