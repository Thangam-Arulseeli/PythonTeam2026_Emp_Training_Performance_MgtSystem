from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Identity,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.employee_document import EmployeeDocument

class EmployeeData(Base):

    __tablename__="employee"

    __table_args__=(

        UniqueConstraint("email",
                        name="unique_email"),

        UniqueConstraint("phone", 
                        name="unique_phone_number"),

        Index("ix_employee_dept_email", "department", "email"),

        Index("ix_employee_is_active", "is_active"),

    )

    employee_id:Mapped[int] = mapped_column(Integer,
                                            Identity(start=100,always=True),
                                            primary_key=True
                                            )

    full_name :Mapped[str] = mapped_column(String(50),
                                           nullable=False 
                                           )
    
    date_of_birth: Mapped[date | None] = mapped_column(Date,
                                                    nullable=True
                                                    )

    email:Mapped[str] = mapped_column(String(300),
                                    nullable=False
                                    )

    phone:Mapped[str] = mapped_column(String(10),
                                    nullable=True
                                    )

    department :Mapped[str] = mapped_column(String(30),
                                            default="Unassigned",
                                            server_default="Unassigned",
                                            nullable=False
                                            )

    role:Mapped[str] = mapped_column(String(9),
                                              default="employee",
                                              server_default="employee",
                                              nullable=False
                                              )

    joining_date:Mapped[date] = mapped_column(Date,
                                            nullable=True
                                            )

    is_active:Mapped[bool] = mapped_column(Boolean,
                                        server_default=text("true"),
                                        nullable=False
                                        )

    created_at :Mapped[datetime] = mapped_column(DateTime,
                                                server_default=text("NOW()"),
                                                nullable=False
                                                )


    documents: Mapped[list["EmployeeDocument"]] = relationship( 
                                                                "EmployeeDocument", 
                                                                back_populates="employee",
                                                                cascade="all, delete-orphan"
                                                            )