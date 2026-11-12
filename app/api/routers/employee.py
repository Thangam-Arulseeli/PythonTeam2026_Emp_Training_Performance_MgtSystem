
from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    Path,
    Query,
    UploadFile,
    status,
)

from app.api.dependencies.employee import (
    EmployeeServiceDep,
    EmployeeDocumentServiceDep,
)

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)

from app.schemas.employee_document import (
    EmployeeDocumentResponse,
)


router = APIRouter(
    prefix="/api/employees",
    tags=["Employee Management"],
)


# CREATE EMPLOYEE
@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
    data: EmployeeCreate,
    service: EmployeeServiceDep,
):
    return await service.create_employee(data)


# DISPLAY ALL ACTIVE EMPLOYEES
@router.get(
    "/",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_employees(
    service: EmployeeServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await service.get_all_employees(
        skip=skip,
        limit=limit,
    )


# DISPLAY EMPLOYEE BY ID
@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_employee_by_id(
    
    service: EmployeeServiceDep,
    employee_id: int = Path(gt=0),
):
    return await service.get_employee_by_id(
        employee_id
    )


# UPDATE EMPLOYEE USING PATCH
@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
async def update_employee(
    data: EmployeeUpdate,
    service: EmployeeServiceDep,
    employee_id: int = Path(gt=0),
):
    return await service.update_employee(
        employee_id=employee_id,
        data=data,
    )


# SOFT DELETE EMPLOYEE
@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_employee(
    service: EmployeeServiceDep,
    employee_id: int = Path(gt=0),
):
    await service.delete_employee(employee_id)


# UPLOAD PROFILE PICTURE AND RESUME
@router.post(
    "/{employee_id}/documents",
    response_model=list[EmployeeDocumentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_employee_documents(
    service: EmployeeDocumentServiceDep,
    profile_picture: Annotated[UploadFile, File()],
    resume: Annotated[UploadFile, File()],
    employee_id: int = Path(gt=0),
):
    return await service.upload_documents(
        employee_id=employee_id,
        profile_picture=profile_picture,
        resume=resume,
    )


# GET EMPLOYEE DOCUMENTS
@router.get(
    "/{employee_id}/documents",
    response_model=list[EmployeeDocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_employee_documents(
    service: EmployeeDocumentServiceDep,
    employee_id: int = Path(gt=0),
):
    return await service.get_documents(employee_id)
