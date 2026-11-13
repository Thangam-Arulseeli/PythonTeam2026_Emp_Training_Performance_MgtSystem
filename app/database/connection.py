"""
Asynchronous Database Engine Configuration.

Creates and configures the SQLAlchemy asynchronous engine
"""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings

#Load database configuration from application settings
settings = get_settings()

#Validate that the database URL is configured
if not settings.database_url :
    raise RuntimeError("DATABASE_URL is not set. Check your .env file.")

#create a new engine 
engine:AsyncEngine = create_async_engine ( 
                        settings.database_url , 
                        pool_size=settings.db_pool_size,
                        max_overflow=settings.db_max_overflow,
                        pool_timeout=settings.db_pool_timeout,
                        pool_recycle=1800,
                        pool_pre_ping=True,
                        echo=False, 
                    )

