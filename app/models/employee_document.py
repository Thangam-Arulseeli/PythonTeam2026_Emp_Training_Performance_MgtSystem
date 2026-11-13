from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.employee import EmployeeData


class EmployeeDocument(Base):

    __tablename__ = "employee_documents"

    __table_args__ = (
        CheckConstraint(
            "document_type IN ('profile_picture', 'resume')",
            name="ck_employee_document_type",
        ),
        Index("ix_employee_documents_employee_id", "employee_id"),
        Index("ix_employee_documents_type", "document_type"),
    )

    document_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True
    )

    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employee.employee_id"), nullable=False
    )

    document_type: Mapped[str] = mapped_column(String(30), nullable=False)

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    employee: Mapped["EmployeeData"] = relationship(
        "EmployeeData", back_populates="documents"
    )
