"""Dependency injection configuration for Employee Management."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session

# Repository implementations
from app.repositories.implementations.employee_document_repository import (
    EmployeeDocumentRepositoryImpl,
)
from app.repositories.implementations.employee_repository import (
    EmployeeRepositoryImpl,
)

# Repository interfaces
from app.repositories.interfaces.employee_document_interface import (
    EmployeeDocumentRepositoryInterface,
)
from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface,
)
from app.services.implementations.employee_document_service import (
    EmployeeDocumentServiceImpl,
)

# Service implementations
from app.services.implementations.employee_service import (
    EmployeeServiceImpl,
)
from app.services.interfaces.employee_document_service import (
    EmployeeDocumentServiceInterface,
)

# Service interfaces
from app.services.interfaces.employee_service import (
    EmployeeServiceInterface,
)


# EMPLOYEE REPOSITORY DEPENDENCY
def get_employee_repository(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> EmployeeRepositoryInterface:
    """Provide the employee repository implementation."""

    return EmployeeRepositoryImpl(db=db)


# EMPLOYEE DOCUMENT REPOSITORY DEPENDENCY
def get_employee_document_repository(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> EmployeeDocumentRepositoryInterface:
    """Provide the employee document repository implementation."""

    return EmployeeDocumentRepositoryImpl(db=db)


# EMPLOYEE SERVICE DEPENDENCY
def get_employee_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[
        EmployeeRepositoryInterface,
        Depends(get_employee_repository),
    ],
) -> EmployeeServiceInterface:
    """Provide the employee service implementation."""

    return EmployeeServiceImpl(
        db=db,
        repository=repository,
    )


# EMPLOYEE DOCUMENT SERVICE DEPENDENCY
def get_employee_document_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    employee_repository: Annotated[
        EmployeeRepositoryInterface,
        Depends(get_employee_repository),
    ],
    document_repository: Annotated[
        EmployeeDocumentRepositoryInterface,
        Depends(get_employee_document_repository),
    ],
) -> EmployeeDocumentServiceInterface:
    """Provide the employee document service implementation."""

    return EmployeeDocumentServiceImpl(
        db=db,
        employee_repository=employee_repository,
        document_repository=document_repository,
    )


# REUSABLE SERVICE DEPENDENCIES
EmployeeServiceDep = Annotated[
    EmployeeServiceInterface,
    Depends(get_employee_service),
]

EmployeeDocumentServiceDep = Annotated[
    EmployeeDocumentServiceInterface,
    Depends(get_employee_document_service),
]
