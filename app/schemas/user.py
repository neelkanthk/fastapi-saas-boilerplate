from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    country: Optional[str] = None
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    subscriptions: Optional[list[dict]] = None
    notifications: Optional[list[dict]] = None


class UserProfileCreateRequest(BaseModel):
    full_name: Optional[str] = None
    country: Optional[str] = None


class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    country: Optional[str] = None


class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdatePasswordResponse(BaseModel):
    message: str
