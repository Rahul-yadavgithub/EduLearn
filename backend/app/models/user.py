from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


# ---------- BASE ----------
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str  # student | teacher | admin


# ---------- REQUEST ----------
class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------- DB MODEL ----------
class User(UserBase):
    model_config = ConfigDict(extra="ignore")

    user_id: str
    picture: Optional[str] = None
    created_at: datetime
    is_approved: bool = True


# ---------- RESPONSE ----------
class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    role: str
    picture: Optional[str] = None
    is_approved: bool = True


class TokenResponse(BaseModel):
    token: str
    user: UserResponse
