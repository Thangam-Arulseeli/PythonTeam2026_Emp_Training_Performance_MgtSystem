
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee_document import EmployeeDocument
from app.repositories.interfaces.employee_document_interface import (
    EmployeeDocumentRepositoryInterface,
)


class EmployeeDocumentRepositoryImpl( EmployeeDocumentRepositoryInterface ):

    def __init__(self, db: AsyncSession):
        self.db = db

    # UPLOAD PROFILE PICTURE OR RESUME RECORDS OR BOTH 
    async def create_documents(
        self,
        documents: list[EmployeeDocument]
    ) -> list[EmployeeDocument]:

        """upload either profile pic or the resume or both"""

        self.db.add_all(documents)

        await self.db.flush()

        return documents

    # GET EMPLOYEE DOCUMENTS
    async def get_documents_by_employee_id(
        self,
        employee_id: int
    ) -> list[EmployeeDocument]:

        """Retrieve the uploaded documents of an employee."""

        statement = (
            select(EmployeeDocument)
            .where(
                EmployeeDocument.employee_id == employee_id
            )
            .order_by(EmployeeDocument.document_id)
        )

        result = await self.db.execute(statement)

        return list(result.scalars().all())
