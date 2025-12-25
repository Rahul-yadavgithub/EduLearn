from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth import TeacherApprovalRequest
from app.core.db import db
from app.core.security import get_admin_user
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/pending-teachers")
async def pending_teachers(admin=Depends(get_admin_user)):
    return await db.users.find(
        {"role": "teacher", "is_approved": False},
        {"_id": 0, "password": 0}
    ).to_list(100)


@router.post("/approve-teacher")
async def approve_teacher(data: TeacherApprovalRequest, admin=Depends(get_admin_user)):
    result = await db.users.update_one(
        {"user_id": data.user_id, "role": "teacher"},
        {"$set": {"is_approved": data.approve}}
    )

    if not result.modified_count:
        raise HTTPException(404, "Teacher not found")

    await db.notifications.insert_one({
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": data.user_id,
        "message": "Teacher approved" if data.approve else "Approval revoked",
        "type": "teacher_approved",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"message": "Teacher approval updated"}
