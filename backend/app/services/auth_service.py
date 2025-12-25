from fastapi import HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
import uuid, httpx

from app.core.database import db
from app.core.security import (
    hash_password,
    verify_password,
    create_token,
)
from app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD


# -------------------------------------------------
# REGISTER
# -------------------------------------------------
async def register_user(data):
    if await db.users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"user_{uuid.uuid4().hex[:12]}"
    is_approved = data.role != "teacher"

    user_doc = {
        "user_id": user_id,
        "email": data.email,
        "name": data.name,
        "role": data.role,
        "password": hash_password(data.password),
        "picture": None,
        "is_approved": is_approved,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.users.insert_one(user_doc)

    return {
        "token": create_token(user_id),
        "user": {
            "user_id": user_id,
            "email": data.email,
            "name": data.name,
            "role": data.role,
            "picture": None,
            "is_approved": is_approved,
        },
    }


# -------------------------------------------------
# LOGIN
# -------------------------------------------------
async def login_user(data):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})

    if not user or not user.get("password"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "token": create_token(user["user_id"]),
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "picture": user.get("picture"),
            "is_approved": user.get("is_approved", True),
        },
    }


# -------------------------------------------------
# ADMIN LOGIN
# -------------------------------------------------
async def admin_login(data):
    if data.email != ADMIN_EMAIL or data.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    admin = await db.users.find_one({"email": ADMIN_EMAIL}, {"_id": 0})

    if not admin:
        admin = {
            "user_id": f"admin_{uuid.uuid4().hex[:12]}",
            "email": ADMIN_EMAIL,
            "name": "Admin",
            "role": "admin",
            "password": hash_password(ADMIN_PASSWORD),
            "picture": None,
            "is_approved": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(admin)

    return {
        "token": create_token(admin["user_id"]),
        "user": {
            "user_id": admin["user_id"],
            "email": admin["email"],
            "name": admin["name"],
            "role": admin["role"],
            "picture": None,
            "is_approved": True,
        },
    }


# -------------------------------------------------
# OAUTH / SESSION LOGIN
# -------------------------------------------------
async def process_session_login(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    role = body.get("role", "student")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    async with httpx.AsyncClient() as client:
        auth_response = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id},
        )

    if auth_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session")

    user_data = auth_response.json()

    existing_user = await db.users.find_one(
        {"email": user_data["email"]}, {"_id": 0}
    )

    if existing_user:
        user_id = existing_user["user_id"]
        role = existing_user["role"]
        is_approved = existing_user.get("is_approved", True)
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        is_approved = role != "teacher"

        await db.users.insert_one({
            "user_id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "role": role,
            "picture": user_data.get("picture"),
            "password": None,
            "is_approved": is_approved,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    session_token = user_data["session_token"]
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    await db.user_sessions.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "session_token": session_token,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        upsert=True,
    )

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )

    return {
        "user_id": user_id,
        "email": user_data["email"],
        "name": user_data["name"],
        "role": role,
        "picture": user_data.get("picture"),
        "is_approved": is_approved,
    }


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
async def logout_user(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if token:
        await db.user_sessions.delete_one({"session_token": token})

    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}
