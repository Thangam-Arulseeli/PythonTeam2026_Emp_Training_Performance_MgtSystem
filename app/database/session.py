"""
Creates a SQLAlchemy asynchronous session factory and provides
database sessions to FastAPI endpoints using dependency injection.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.connection import engine

# creating a session factory
SessionLocal = async_sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)


# dependecy creation
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a session that closes automatically when the request finishes."""

    async with SessionLocal() as session:
        yield session
