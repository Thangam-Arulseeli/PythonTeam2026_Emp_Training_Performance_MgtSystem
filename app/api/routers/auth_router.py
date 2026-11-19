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
from app.services.interfaces.auth_service import AuthServiceInterface

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

AuthServiceDependency = Annotated[AuthServiceInterface, Depends(get_auth_service)]
SessionDependency = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDependency = Annotated[User, Depends(get_current_user)]


# register
@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    data: RegisterRequest,
    service: AuthServiceDependency,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> MessageResponse:
    await service.register(db, data)
    return MessageResponse(message="Registration successful. You can now log in.")


# login
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and return tokens",
)
async def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDependency,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    return await service.login(db, data.username, data.password)


# refresh
@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh(
    data: RefreshRequest,
    service: AuthServiceDependency,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    return await service.refresh_tokens(db, data.refresh_token)


# logout
@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Log out and revoke refresh token",
)
async def logout(
    data: RefreshRequest,
    service: AuthServiceDependency,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MessageResponse:
    await service.logout(db, data.refresh_token, current_user.user_id)

    return MessageResponse(message="Logged out successfully.")


# current user profile
@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
