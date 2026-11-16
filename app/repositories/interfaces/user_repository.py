from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_email(
        self,db:AsyncSession,email:str
    )->User |None:
        pass

    @abstractmethod
    async def get_by_username(
        self,db:AsyncSession,username:str
    )->User|None:
        pass


    @abstractmethod
    async def get_by_id(
        self,db:AsyncSession,user_id:int
    )->User|None:
        pass

    @abstractmethod
    async def staff_email_exists(
        self,db:AsyncSession,email:str,role:str
    )->bool:
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
        pass
