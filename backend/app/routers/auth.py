from fastapi import APIRouter, Depends, Request, Response

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
)
from app.core.security import get_current_user
from app.services.auth_service import (
    register_user,
    login_user,
    admin_login,
    process_session_login,
    logout_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# -------------------------------------------------
# REGISTER
# -------------------------------------------------
@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest):
    return await register_user(data)


# -------------------------------------------------
# LOGIN
# -------------------------------------------------
@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    return await login_user(data)


# -------------------------------------------------
# ADMIN LOGIN
# -------------------------------------------------
@router.post("/admin-login", response_model=AuthResponse)
async def login_admin(data: LoginRequest):
    return await admin_login(data)


# -------------------------------------------------
# SESSION LOGIN (OAUTH)
# -------------------------------------------------
@router.post("/session")
async def session_login(request: Request, response: Response):
    return await process_session_login(request, response)


# -------------------------------------------------
# CURRENT USER
# -------------------------------------------------
@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "role": current_user["role"],
        "picture": current_user.get("picture"),
        "is_approved": current_user.get("is_approved", True),
    }


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
@router.post("/logout")
async def logout(request: Request, response: Response):
    return await logout_user(request, response)
