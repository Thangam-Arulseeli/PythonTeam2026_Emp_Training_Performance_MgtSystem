from abc import ABC, abstractmethod

from fastapi import UploadFile
from app.models.employee_document import EmployeeDocument


class EmployeeDocumentServiceInterface(ABC):

    @abstractmethod
    async def check_employee(self, employee_id: int) -> None:
        """Verify whether the employee exists and is active."""
        pass

    @abstractmethod
    async def save_file( self, file: UploadFile, document_type: str ) -> str:
        """VALIDATE AND STORE FILE"""
        pass

    @abstractmethod
    async def upload_documents(
        self,
        employee_id: int,
        profile_picture: UploadFile | None = None,
        resume: UploadFile | None = None,
    ) -> list[EmployeeDocument]:
        """UPLOAD PROFILE PICTURE AND RESUME"""
        pass

    @abstractmethod
    async def get_documents( self, employee_id: int ) -> list[EmployeeDocument]:
        """GET EMPLOYEE DOCUMENTS"""
        pass