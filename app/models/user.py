from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    func
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.refresh_token import RefreshToken

class User(Base):
    __tablename__ = "users"

    __table_args__ =(
        CheckConstraint(
            "role in ('admin','employee','trainer')",
            name="check_user_role"            
        ),
    )

    user_id :Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    username : Mapped[str] =mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    email :Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password :Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role :Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    is_active :Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable= False
    )

    created_at :Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    modified_at :Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

