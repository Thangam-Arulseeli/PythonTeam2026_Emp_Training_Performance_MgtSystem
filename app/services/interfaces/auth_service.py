from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth_schema import RegisterRequest


class AuthServiceInterface(ABC):

    # register user
    @abstractmethod
    async def register(self, db: AsyncSession, data: RegisterRequest) -> None:
        pass            

    # login
    @abstractmethod
    async def login(
        self, db: AsyncSession, username: str, password: str
    ) -> dict[str, str]:
        pass

    # refresh token
    @abstractmethod
    async def refresh_tokens(
        self, db: AsyncSession, refresh_token: str
    ) -> dict[str, str]:
        pass


    # logout
    @abstractmethod
    async def logout(
        self, db: AsyncSession, refresh_token: str, current_user_id: int
    ) -> None:
        pass
