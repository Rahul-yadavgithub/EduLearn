from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.core.database import db
from app.core.security import (
    hash_password,
    verify_password,
    create_token,
    get_current_user
)
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest):
    if await db.users.find_one({"email": data.email}):
        raise HTTPException(400, "Email already registered")

    user_id = f"user_{uuid.uuid4().hex[:12]}"
    is_approved = data.role != "teacher"

    await db.users.insert_one({
        "user_id": user_id,
        "email": data.email,
        "name": data.name,
        "role": data.role,
        "password": hash_password(data.password),
        "picture": None,
        "is_approved": is_approved,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {
        "token": create_token(user_id),
        "user": {
            "user_id": user_id,
            "email": data.email,
            "name": data.name,
            "role": data.role,
            "picture": None,
            "is_approved": is_approved
        }
    }


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")

    return {
        "token": create_token(user["user_id"]),
        "user": {k: user[k] for k in ("user_id", "email", "name", "role", "picture", "is_approved")}
    }


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if token:
        await db.user_sessions.delete_one({"session_token": token})
    response.delete_cookie("session_token")
    return {"message": "Logged out"}
