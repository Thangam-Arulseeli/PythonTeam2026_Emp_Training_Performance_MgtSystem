from fastapi import FastAPI

from app.core.config import get_settings
from app.api.routers.health import router as health_router
from app.api.routers.course import router as course_router
from app.api.routers.batch import router as batch_router
from app.api.routers.course_content import router as course_content_router
from app.exceptions import AppException
from app.exceptions.handlers import app_exception_handler

# Load application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Employee Training and Performance Management System API",
)
app.add_exception_handler(AppException, app_exception_handler)

app.include_router(health_router)
app.include_router(course_router)
app.include_router(batch_router)
app.include_router(course_content_router)
