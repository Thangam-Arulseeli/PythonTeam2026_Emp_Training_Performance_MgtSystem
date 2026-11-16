from fastapi import FastAPI

from app.api.routers.auth_router import router as auth_router
from app.api.routers.employee import router as employee_router
from app.api.routers.health import router as health_router
from app.core.config import get_settings
from app.exceptions.exception_handlers import register_exception_handlers

# Load application settings
settings = get_settings()

# Initialize the FastAPI application with project metadata.
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Employee Training and Performance Management System API"
)

#Register the routers  
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(employee_router)

#Register centralized exception handlers
register_exception_handlers(app)
