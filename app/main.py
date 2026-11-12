from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.trainer_router import router as trainer_router
from app.core.config import get_settings

# Load application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Employee Training and Performance Management System API"
)

app.include_router(health_router)

app.include_router(trainer_router)