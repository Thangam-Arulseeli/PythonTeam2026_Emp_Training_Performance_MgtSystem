"""
Employee Management API Router.
"""

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Path,
    Query,
    UploadFile,
    status,
)

from app.api.dependencies.auth import (
    require_roles,
)
from app.api.dependencies.employee import (
    EmployeeDocumentServiceDep,
    EmployeeServiceDep,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.schemas.employee_document import (
    EmployeeDocumentResponse,
    EmployeeDocumentsListResponse,
)

router = APIRouter(
    prefix="/api/employees",
    tags=["Employee Management"],
)


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin"))],
)
async def create_employee(
    data: EmployeeCreate,
    service: EmployeeServiceDep,
)->EmployeeResponse:
    return await service.create_employee(data)


@router.get(
    "/",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("admin", "employee", "trainer"))]
)
async def get_all_employees(
    service: EmployeeServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
)->list[EmployeeResponse]:
    return await service.get_all_employees( skip=skip,limit=limit,)


@router.get(
    "/inactive_employee",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("admin", "employee", "trainer"))]
)
async def get_all_employees_inactive(
    service: EmployeeServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
)->list[EmployeeResponse]:
    return await service.get_all_employees_inactive( skip=skip,limit=limit,)

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("admin", "employee", "trainer"))]
)
async def get_employee_by_id( 
    service: EmployeeServiceDep,
    employee_id: int = Path(gt=0),
)->EmployeeResponse:
    return await service.get_employee_by_id(employee_id)


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("admin"))],
)
async def update_employee(
    data: EmployeeUpdate,
    service: EmployeeServiceDep,
    employee_id: int = Path(gt=0),
)->EmployeeResponse:
    return await service.update_employee( employee_id=employee_id, data=data,)

@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("admin"))],
)
async def delete_employee(
    service: EmployeeServiceDep,
    employee_id: int = Path(gt=0),
)->dict[str, str|int]:
    return await service.delete_employee(employee_id)

# REACTIVATE INACTIVE EMPLOYEE
@router.put(
    "/{employee_id}/reactivate",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("admin"))],
)
async def reactivate_employee(
    service: EmployeeServiceDep,
    employee_id: int = Path(gt=0),
)->EmployeeResponse:
    
    return await service.reactivate_employee(employee_id)


@router.post(
    "/{employee_id}/documents",
    response_model=list[EmployeeDocumentResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin"))],
)
async def upload_employee_documents(
    service: EmployeeDocumentServiceDep,
    profile_picture: Annotated[UploadFile | None, File()]= None,
    resume: Annotated[UploadFile | None, File()]= None,
    employee_id: int = Path(gt=0),
)->list[EmployeeDocumentResponse]:
    return await service.upload_documents(
        employee_id=employee_id,
        profile_picture=profile_picture,
        resume=resume,
    )


@router.get(
    "/{employee_id}/documents",
    response_model=EmployeeDocumentsListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("admin", "employee", "trainer"))]
)
async def get_employee_documents(
    service: EmployeeDocumentServiceDep,
    employee_id: int = Path(gt=0),
)->EmployeeDocumentsListResponse:
    documents = await service.get_documents(employee_id)

    if not documents:
        return {
            "message": "Employee exists but no documents uploaded",
            "employee_id": employee_id,
            "documents": [],
        }

    return {
        "message": "Employee documents retrieved successfully",
        "employee_id": employee_id,
        "documents": [
            EmployeeDocumentResponse.model_validate(doc)
            for doc in documents
        ],
    }