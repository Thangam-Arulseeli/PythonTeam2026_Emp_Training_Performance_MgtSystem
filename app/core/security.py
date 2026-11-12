import hashlib
from datetime import UTC,datetime,timedelta
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

settings = get_settings()
password_hash = PasswordHash.recommended()

def hash_password(password:str) ->str:
    return password_hash.hash(password)


def verify_password(plain_password:str,hashed_password:str) -> bool:
    return password_hash.verify(plain_password,hashed_password)

def create_token(
    user_id:int,
    role:str,
    token_type:str,
    expires_delta:timedelta
)->tuple[str,datetime]:
    now = datetime.now(UTC)
    expires_at = now+expires_delta
    jti = str(uuid4())
    payload :dict ={
        "sub":str(user_id),
        "role" :role,
        "type" :token_type,
        "jti":jti,
        "iat":now,
        "exp":expires_at
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return token,expires_at

def create_access_token(user_id:int,role:str)->str:
    token ,_=create_token(
        user_id=user_id,
        role=role,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return token

def create_refresh_token(user_id:int,role:str)->str:
    return create_token(
        user_id=user_id,
        role=role,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days)
    )

def decode_token(token:str)->dict:
    return jwt.decode(
        token,settings.jwt_secret_key,algorithms=[settings.jwt_algorithm]
    )

def hash_refresh_token(token:str) ->dict:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
