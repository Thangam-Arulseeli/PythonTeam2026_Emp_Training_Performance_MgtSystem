from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken

class RefreshTokenRepositoryInterface(ABC):

    @abstractmethod
    async def create(
        self,
        db: AsyncSession,
        user_id: int,
        token_hash: str,
        expires_at: datetime
    ) -> RefreshToken:
        pass

    @abstractmethod
    async def get_valid_for_update(
        self,
        db: AsyncSession,
        token_hash: str
    ) -> RefreshToken | None:
        pass
