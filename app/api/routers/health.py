from typing import Annotated

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
    db: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        result = await db.execute(text("SELECT 1"))

        if result.scalar_one() == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "message": "Database connection successful"
            }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc

