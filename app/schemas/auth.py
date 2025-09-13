from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str


class UserRegistrationResponse(BaseModel):
    id: int
    email: EmailStr


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


# For refresh endpoint
class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
