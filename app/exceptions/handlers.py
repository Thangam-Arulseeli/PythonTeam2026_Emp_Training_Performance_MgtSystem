from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import AppException
from app.utils.logger import logger


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", "N/A")
    logger.warning(
        "AppException on %s %s | Status: %s | Detail: %s | Correlation ID: %s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
        correlation_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", "N/A")
    logger.exception(
        "Unhandled error on %s %s | Correlation ID: %s | Error: %s",
        request.method,
        request.url.path,
        correlation_id,
        str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )
