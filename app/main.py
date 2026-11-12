from fastapi import FastAPI

from app.core.config import get_settings
from app.routers.health import router as health_router
from app.api.routers.auth_router import router as auth_router

# Load application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Employee Training and Performance Management System API"
)

app.include_router(health_router)
app.include_router(auth_router)
