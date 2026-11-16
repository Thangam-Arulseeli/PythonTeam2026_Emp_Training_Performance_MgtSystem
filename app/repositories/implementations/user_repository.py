from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import EmployeeData
from app.models.trainer import Trainer
from app.models.user import User
from app.repositories.interfaces.user_repository import UserRepositoryInterface


class UserRepository(UserRepositoryInterface):
    async def get_by_email(self, db:AsyncSession, email:str) ->User|None:
        result = await db.execute(
            select(User)
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, db:AsyncSession, username:str) ->User|None:
        result = await db.execute(
            select(User)
            .where(User.username == username)
        )
        return result.scalar_one_or_none()


    async def get_by_id(self, db:AsyncSession, user_id:int)->User|None:
        result = await db.execute(
            select(User)
            .where(User.user_id == user_id)
        )

        return result.scalar_one_or_none()

    async def staff_email_exists(self, db:AsyncSession, email:str, role:str)->bool:
        if role == "employee":
            query = select(EmployeeData).where(
                EmployeeData.email == email,
                EmployeeData.is_active.is_(True)
            )

        elif role == "trainer":
            query = select(Trainer).where(
                Trainer.email == email,
                Trainer.is_active.is_(True)
            )

        else:
            return False

        result = await db.execute(query)

        return result.scalar_one_or_none() is not None


    async def create_user(self, 
        db:AsyncSession, 
        username:str, 
        email:str, 
        hashed_password:str, 
        role:str
    ):
        user =User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active =True
        )
        db.add(user)
        await db.flush()
        return user