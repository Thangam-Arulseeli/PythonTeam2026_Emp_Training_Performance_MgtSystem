import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.utils.logger import logger


async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Log request and response details as they pass through the application.

    This middleware supports monitoring and troubleshooting.
    """
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    start_time = time.perf_counter()

    logger.info(
        "Request started: %s %s | Correlation ID: %s",
        request.method,
        request.url.path,
        correlation_id,
    )

    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        response.headers["X-Correlation-ID"] = correlation_id

        logger.info(
            "Request completed: %s %s | Status: %s | Time: %.4f seconds | Correlation ID: %s",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            correlation_id,
        )

        return response
    except Exception as exc:
        process_time = time.perf_counter() - start_time
        logger.exception(
            "Request failed: %s %s | Time: %.4f seconds | Correlation ID: %s | Error: %s",
            request.method,
            request.url.path,
            process_time,
            correlation_id,
            str(exc),
        )
        raise exc
