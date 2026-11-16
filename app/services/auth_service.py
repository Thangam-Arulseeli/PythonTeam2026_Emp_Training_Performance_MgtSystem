from datetime import UTC, datetime

import jwt
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.repositories.interfaces.refresh_token_repository import (
    RefreshTokenRepositoryInterface,
)
from app.repositories.interfaces.user_repository import UserRepositoryInterface
from app.utils.logger import logger


class AuthService:
    def __init__(
        self,
        user_repository:UserRepositoryInterface,
        refresh_token_repository:RefreshTokenRepositoryInterface
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    # register user
    async def register(self,db:AsyncSession,data)->None:
        try:

            #only employee and trainer can register
            if data.role not in {"employee","trainer"}:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only employees and trainers can register."
                )

            #verifying the mail in existing trainer and employee table
            if not await self.user_repository.staff_email_exists(
                db,data.email,data.role
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Email is not registered as an active {data.role}"
                )

            # cheking duplicate email,username
            if await self.user_repository.get_by_email(
                db,data.email
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email is already registered."
                )

            if await self.user_repository.get_by_username(
                db,data.username
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username is already taken"
                )


            hashed_password= hash_password(data.password)

            await self.user_repository.create_user(
                db,
                username=data.username,
                email=data.email,
                hashed_password=hashed_password,
                role=data.role
            )
            logger.info("User registered successfully")
            await db.commit()

        except HTTPException:
            await db.rollback()
            raise

        except IntegrityError:
            await db.rollback()
            logger.exception("Registration failed")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email is already registered."
            )


        except SQLAlchemyError:
            await db.rollback()
            logger.exception("Registration failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to complete registration"
            ) 


    # login
    async def login(self,db:AsyncSession,username:str,password:str):
        user = await self.user_repository.get_by_username(db,username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        if not verify_password(password,user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        access_token = create_access_token(
            user_id=user.user_id,
            role=user.role
        )
        refresh_token,expires_at = create_refresh_token(
            user_id=user.user_id,
            role=user.role
        )
        try:
            await self.refresh_token_repository.create(
                db,
                user_id=user.user_id,
                token_hash=hash_refresh_token(refresh_token),
                expires_at=expires_at
            )
            await db.commit()
            logger.info("User logged in sucessfully")

        except SQLAlchemyError:
            await db.rollback()
            logger.exception("Unable to complete log in")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to complete login."
            )

        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":"bearer"
        }

    # refresh token
    async def refresh_tokens(self,db:AsyncSession,refresh_token:str)->dict[str,str]:
        try:
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise ValueError("Wrong token type")

            user_id = int(payload["sub"])

        except (jwt.PyJWTError,ValueError,KeyError,TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        try:
            stored_token =(
                await self.refresh_token_repository.get_valid_for_update(
                    db,hash_refresh_token(refresh_token)
                )
            )
            if stored_token is None or stored_token.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token is invalid, expired or already used."
                )

            user = await self.user_repository.get_by_id(db,user_id=user_id)
            if user is None or not user.is_active:

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is unavailable."
                )

            stored_token.revoked_at= datetime.now(UTC)

            # generate new tokens
            new_access_token = create_access_token(
                user.user_id,
                user.role
            )
            new_refresh_token, expires_at = create_refresh_token(
                user.user_id,
                user.role
            )

            await self.refresh_token_repository.create(
                db,
                user.user_id,
                hash_refresh_token(new_refresh_token),
                expires_at
            )
            await db.commit()
            logger.info("New access and refresh token created")

        except HTTPException:
            await db.rollback()
            logger.exception("Unable to refresh token")
            raise

        except SQLAlchemyError:
            await db.rollback()
            logger.exception("Unable to refresh token")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to refresh session."
            )
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    # logout
    async def logout(
        self,
        db: AsyncSession,
        refresh_token: str,
        current_user_id: int
    ) -> None:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Wrong token type")

            token_user_id = int(payload["sub"])

        except (jwt.PyJWTError, ValueError, KeyError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token."
            ) 

        if token_user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token does not belong to current user."
            )

        try:
            stored_token = (
                await self.refresh_token_repository.get_valid_for_update(
                    db,hash_refresh_token(refresh_token)
                )
            )
            if stored_token is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token is invalid or already revoked."
                )

            stored_token.revoked_at = datetime.now(UTC)
            await db.commit()
            logger.info("User logged out successfully..")

        except HTTPException:
            await db.rollback()
            logger.exception("Logout failed")
            raise

        except SQLAlchemyError:
            await db.rollback()
            logger.exception("Logout failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to log out."
            )




