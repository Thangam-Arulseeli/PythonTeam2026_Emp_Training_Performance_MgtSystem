from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken

from app.repositories.interfaces.refresh_token_repository import (
    RefreshTokenRepositoryInterface
)

class RefreshTokenRepository(RefreshTokenRepositoryInterface):
    async def create(
        self,
        db: AsyncSession,
        user_id: int,
        token_hash: str,
        expires_at: datetime
    ) -> RefreshToken:
        """Add a refresh-token record and flush it into the current transaction."""
        
        token_record = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        db.add(token_record)
        await db.flush()
        return token_record

    async def get_valid_for_update(
        self,
        db: AsyncSession,
        token_hash: str
    ) -> RefreshToken | None:
        """Lock and return an unrevoked, unexpired refresh token by its hash."""
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > datetime.now(UTC)
            ).with_for_update()
        )

        return result.scalar_one_or_none()
