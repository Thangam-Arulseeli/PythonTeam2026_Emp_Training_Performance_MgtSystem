from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_email(
        self,db:AsyncSession,email:str
    )->User |None:
        """Find a user by email address."""
        pass

    @abstractmethod
    async def get_by_username(
        self,db:AsyncSession,username:str
    )->User|None:
        """Find a user by username."""
        pass


    @abstractmethod
    async def get_by_id(
        self,db:AsyncSession,user_id:int
    )->User|None:
        """Find a user by primary key."""
        pass

    @abstractmethod
    async def staff_email_exists(
        self,db:AsyncSession,email:str,role:str
    )->bool:
        """Check for an active employee or trainer record with the email and role."""
        pass

    @abstractmethod
    async def create_user(
        self,
        db:AsyncSession,
        username:str,
        email:str,
        hashed_password:str,
        role:str
    )->User:
        """Add a user record to the active database session."""
        pass
