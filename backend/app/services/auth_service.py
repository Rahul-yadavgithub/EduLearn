from fastapi import HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
import uuid, jwt, bcrypt, httpx
from app.core.db import db
from app.core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS, ADMIN_EMAIL, ADMIN_PASSWORD


# ---------- PASSWORD ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ---------- JWT ----------
def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ---------- AUTH ----------
async def register_user(data):
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


async def login_user(data):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")

    return {
        "token": create_token(user["user_id"]),
        "user": {k: user[k] for k in ("user_id", "email", "name", "role", "picture", "is_approved")}
    }


async def admin_login(data):
    if data.email != ADMIN_EMAIL or data.password != ADMIN_PASSWORD:
        raise HTTPException(401, "Invalid admin credentials")

    admin = await db.users.find_one({"email": ADMIN_EMAIL}, {"_id": 0})
    if not admin:
        admin = {
            "user_id": f"admin_{uuid.uuid4().hex[:12]}",
            "email": ADMIN_EMAIL,
            "name": "Admin",
            "role": "admin",
            "password": hash_password(ADMIN_PASSWORD),
            "is_approved": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin)

    return {
        "token": create_token(admin["user_id"]),
        "user": admin
    }


async def get_current_user(request: Request):
    token = request.cookies.get("session_token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(401, "Not authenticated")

    session = await db.user_sessions.find_one({"session_token": token})
    if session:
        if datetime.fromisoformat(session["expires_at"]) < datetime.now(timezone.utc):
            raise HTTPException(401, "Session expired")
        return await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"user_id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(401)
        return user
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")


async def get_admin_user(request: Request):
    user = await get_current_user(request)
    if user["role"] != "admin":
        raise HTTPException(403)
    return user
