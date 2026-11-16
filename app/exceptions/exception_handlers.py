
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.exceptions import (
    EmployeeAlreadyExistsException,
    EmployeeInactiveException,
    EmployeeNotFoundException,
    InvalidEmployeeDataException,
)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(EmployeeNotFoundException)
    async def employee_not_found_handler(
        request: Request,
        exc: EmployeeNotFoundException
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": exc.message}
        )

    @app.exception_handler(EmployeeAlreadyExistsException)
    async def employee_exists_handler(
        request: Request,
        exc: EmployeeAlreadyExistsException
    ):
        return JSONResponse(
            status_code=409,
            content={"detail": exc.message}
        )

    @app.exception_handler(EmployeeInactiveException)
    async def employee_inactive_handler(
        request: Request,
        exc: EmployeeInactiveException
    ):
        return JSONResponse(
            status_code=409,
            content={"detail": exc.message}
        )

    @app.exception_handler(InvalidEmployeeDataException)
    async def invalid_employee_handler(
        request: Request,
        exc: InvalidEmployeeDataException
    ):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.message}
        )
