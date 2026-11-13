
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
async def health_check(
    session: AsyncSession = Depends(get_session)
):
    """Check that the API can execute a query against its configured database."""
    try:
        result = await session.execute(text("SELECT 1"))

        if result.scalar_one() == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "message": "Database connection successful"
            }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "message": "Database connection failed"
            }
        )
