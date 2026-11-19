from app.repositories.implementations.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.implementations.user_repository import UserRepository
from app.services.implementations.auth_service import AuthService
from app.services.interfaces.auth_service import AuthServiceInterface


def get_auth_service() -> AuthServiceInterface:
    """Build the authentication service with user and refresh-token repositories."""
    return AuthService(
        user_repository=UserRepository(),
        refresh_token_repository=RefreshTokenRepository(),
    )
