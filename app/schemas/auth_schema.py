from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)

class RegisterRequest(BaseModel):
    username :str =Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$"
    )
    email:EmailStr
    password:str =Field(
        min_length=8,
        max_length=50
    )
    role :Literal["employee","trainer"]

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token:str = Field(
        min_length=20,
        max_length=4096
    )

class MessageResponse(BaseModel):
    message:str

class UserProfileResponse(BaseModel):
    user_id:int
    username:str
    email:str
    role:str
    is_active:bool
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)


