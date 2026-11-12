
from abc import ABC, abstractmethod

from app.models.employee_document import EmployeeDocument


class EmployeeDocumentRepositoryInterface(ABC):

    @abstractmethod
    async def create_documents( self, documents: list[EmployeeDocument] ) -> list[EmployeeDocument]:
        pass

    @abstractmethod
    async def get_documents_by_employee_id(  self, employee_id: int) -> list[EmployeeDocument]:
        pass
