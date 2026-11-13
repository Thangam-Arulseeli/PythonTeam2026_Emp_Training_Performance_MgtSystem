
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.implementations.employee_document_repository import (
    EmployeeDocumentRepositoryImpl,
)
from app.repositories.implementations.employee_repository import EmployeeRepositoryImpl
from app.repositories.interfaces.employee_document_interface import (
    EmployeeDocumentRepositoryInterface,
)
from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface,
)
from app.services.employee_document_service import (
    EmployeeDocumentService,
)
from app.services.employee_service import EmployeeService


# EMPLOYEE REPOSITORY DEPENDENCY
def get_employee_repository(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> EmployeeRepositoryInterface:

    return EmployeeRepositoryImpl(db=db)


# EMPLOYEE DOCUMENT REPOSITORY DEPENDENCY
def get_employee_document_repository(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> EmployeeDocumentRepositoryInterface:

    return EmployeeDocumentRepositoryImpl(db=db)


# EMPLOYEE SERVICE DEPENDENCY
def get_employee_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[  EmployeeRepositoryInterface, Depends(get_employee_repository), ],
) -> EmployeeService:

    return EmployeeService( db=db, repository=repository,)


# EMPLOYEE DOCUMENT SERVICE DEPENDENCY
def get_employee_document_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    employee_repository: Annotated[  EmployeeRepositoryInterface, Depends(get_employee_repository), ],
    document_repository: Annotated[ EmployeeDocumentRepositoryInterface, Depends(get_employee_document_repository),],
) -> EmployeeDocumentService:

    return EmployeeDocumentService(
        db=db,
        employee_repository=employee_repository,
        document_repository=document_repository,
    )


# REUSABLE SERVICE DEPENDENCIES
EmployeeServiceDep = Annotated[EmployeeService,Depends(get_employee_service),]

EmployeeDocumentServiceDep = Annotated[ EmployeeDocumentService, Depends(get_employee_document_service),]
