from fastapi import FastAPI

from app.api.routers import (
    attendance_session_router,
    auth_router,
    batch_router,
    course_content_router,
    course_router,
    enrollment_router,
    health_router,
    attendance_record_router,
)
from app.api.routers.employee import router as employee_router
from app.api.routers.trainer_resume_router import router as trainer_resume_router
from app.api.routers.trainer_router import router as trainer_router
from app.core.config import get_settings
from app.exceptions.custom_exceptions import AppException
from app.exceptions.exception_handlers import register_exception_handlers
from app.exceptions.handlers import (
    app_exception_handler,
    global_exception_handler,
)
from app.middleware.request_logging import log_requests

# Load application settings
settings = get_settings()

# Initialize the FastAPI application with project metadata.
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Employee Training and Performance Management System API",
)

# Register the routers
# Register request logging middleware
app.middleware("http")(log_requests)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(employee_router)

# Register centralized exception handlers
register_exception_handlers(app)
app.include_router(course_router)
app.include_router(batch_router)
app.include_router(course_content_router)

app.include_router(trainer_router)
app.include_router(trainer_resume_router)

app.include_router(enrollment_router)


app.include_router(attendance_session_router)
app.include_router(attendance_record_router)
