from app.repositories.implementations.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.implementations.user_repository import UserRepository
from app.services.auth_service import AuthService


def get_auth_service() -> AuthService:
    return AuthService(
        user_repository=UserRepository(),
        refresh_token_repository=RefreshTokenRepository()
    )
