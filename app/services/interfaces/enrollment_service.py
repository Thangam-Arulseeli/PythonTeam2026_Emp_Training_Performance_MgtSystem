from abc import ABC, abstractmethod

from app.models.user import User
from app.schemas.enrollment_schema import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentStatusUpdate,
    EnrollmentStatus,
    EnrollmentListResponse,
    BatchEnrollmentListResponse
)


class EnrollmentServiceInterface(ABC):

    @abstractmethod
    async def create_enrollment(
        self, payload: EnrollmentCreate,
        current_user: User
    ) -> EnrollmentResponse:
        pass

    @abstractmethod
    async def get_enrollment(
        self, 
        enrollment_id: int ,
        current_user : User
    )-> EnrollmentResponse:
        pass

    @abstractmethod
    async def list_enrollments(
        self,
        page:int,
        size:int,
        status: EnrollmentStatus,
        current_user : None
    )-> EnrollmentListResponse:
        pass

    @abstractmethod
    async def get_enrollments_by_employee(
        self,
        employee_id:int,
        current_user: User
    )->list[EnrollmentResponse]:
        pass

    @abstractmethod
    async def get_enrollments_by_batch(
        self,
        batch_id: int,
        page: int,
        size: int,
        current_user: User
    ) -> BatchEnrollmentListResponse:
        pass

