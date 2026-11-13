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

#Configure the Employee Management API router to group related APIs under Employee Management.
router = APIRouter(
    prefix="/api/employees",
    tags=["Employee Management"],
)


#CREATE EMPLOYEE
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

    """router that alllows only the admin to create a new employee """

    return await service.create_employee(data)


#DISPLAY ALL ACTIVE EMPLOYEES 
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

    """router that display all the active employee using pagination"""

    return await service.get_all_employees( skip=skip,limit=limit,)


#DISPLAY ALL INACTIVE EMPLOYEES
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

    """router that display all the inactive employee using pagination"""

    return await service.get_all_employees_inactive( skip=skip,limit=limit,)


#DISPLAY EMPLOYEE BY ID
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

    """router that display all the active employee using employee id """

    return await service.get_employee_by_id(employee_id)


#UPDATE EMPLOYEE DETAILS USING PATCH
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

    """router that allows only the admin to change the employee personal details """

    return await service.update_employee( employee_id=employee_id, data=data,)


#SOFT DELETE EMPLOYEE - MAKE EMPLOYEE INACTIVE
@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("admin"))],
)
async def delete_employee(
    service: EmployeeServiceDep,
    employee_id: int = Path(gt=0),
)->dict[str, str|int]:

    """Allows only the admin to soft-delete an employee by changing the employee's status to inactive.

    If the employee is also registered as a user, the corresponding
    user account is deactivated to prevent the inactive employee
    from logging in or accessing protected APIs
    
    """

    return await service.delete_employee(employee_id)


# UPDATE THE INACTIVE EMPLOYEE TO ACTIVE EMPLOYEE
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

    """Allows only the admin to update the inactive employee to active employee"""
    
    return await service.reactivate_employee(employee_id)


#UPLOAD THE RESUME , PROFILE PIC OR BOTH
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

    """Allows only the admin to upload either profile pic or the resume or both"""

    return await service.upload_documents(
        employee_id=employee_id,
        profile_picture=profile_picture,
        resume=resume,
    )

#GET THE UPLOADED FILES USING EMPLOYEE ID 
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

    """
    Retrieve the uploaded documents of an employee.

    employee exists and has uploaded documents : return  file paths.
    employee exists but has no uploaded documents : return a message indicating that no documents are available.
    employee does not exist or is inactive : raise EmployeeNotFoundException.

    """
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