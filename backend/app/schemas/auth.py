from pydantic import BaseModel, EmailStr
from typing import Optional


# ---------- REQUEST ----------
class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    role: str  # student | teacher
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TeacherApprovalRequest(BaseModel):
    user_id: str
    approve: bool


# ---------- RESPONSE ----------
class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    role: str
    picture: Optional[str] = None
    is_approved: bool = True


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


class MeResponse(UserResponse):
    pass
