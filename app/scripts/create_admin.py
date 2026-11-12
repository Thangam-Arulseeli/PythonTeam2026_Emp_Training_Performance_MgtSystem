import asyncio
from getpass import getpass

from sqlalchemy import or_,select
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.user import User

async def main() ->None:
    username = input("Admin username :").strip()
    email = input("Admin email :").strip()
    password = getpass("Admin password :")
    confirm_password = getpass("Confirm password :")

    if password != confirm_password:
        raise SystemExit("Passwords do not match")

    if not 8 <= len(password) <= 50:
        raise SystemExit("Password must be between 8 and 50 characters")
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(
                or_(
                    User.username == username,
                    User.email == email
                )
            )
        )

        if result.scalar_one_or_none() is not None:
            raise SystemExit("Username or email already registered")

        hashed_password = await asyncio.to_thread(hash_password,password)

        admin = User(
            username = username,
            email = email,
            hashed_password = hashed_password,
            role="admin",
            is_active =True
        )

        db.add(admin)

        try:
            await db.commit()

        except IntegrityError as exc:
            await db.rollback()
            raise SystemExit(
                "Could not create administrator . username or email may already exist."
            ) from exc

    print("Administrator created successfully..")

if __name__ == "__main__":
    asyncio.run(main())


