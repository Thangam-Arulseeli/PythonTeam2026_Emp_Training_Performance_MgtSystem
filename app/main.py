from fastapi import FastAPI

from app.api.routers import (
    auth_router,
    batch_router,
    course_content_router,
    course_router,
    health_router,
)
from app.core.config import get_settings
from app.exceptions.custom_exceptions import AppException
from app.exceptions.handlers import (
    app_exception_handler,
    global_exception_handler,
)
from app.middleware.request_logging import log_requests

# Load application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Employee Training and Performance Management System API",
)

# Register request logging middleware
app.middleware("http")(log_requests)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(course_router)
app.include_router(batch_router)
app.include_router(course_content_router)
