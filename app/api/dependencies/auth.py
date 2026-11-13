from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database.session import get_session
from app.models.user import User
from app.repositories.implementations.user_repository import UserRepository

auth_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)
user_repository = UserRepository()

async def get_current_user(
    token: Annotated[str, Depends(auth_scheme)],
    db: Annotated[AsyncSession, Depends(get_session)],
)-> User:
    try:
        payload=decode_token(token)

        if payload.get("type") != "access":
            raise ValueError("Access token required")

        user_id = int(payload["sub"])

    except (jwt.PyJWTError ,ValueError, KeyError, TypeError) as exc:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate":"Bearer"}
        ) from exc

    user = await user_repository.get_by_id(db,user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive."
        )

    return user



def require_roles(*allowed_roles:str):
    async def role_checker(
            current_user: Annotated[User, Depends(get_current_user)], 
    )-> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You dont have permission to perform this action."
            )

        return current_user

    return role_checker


