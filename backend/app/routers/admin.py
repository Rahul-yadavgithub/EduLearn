from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import uuid

from app.core.database import db
from app.core.security import get_admin_user
from app.schemas.auth import TeacherApprovalRequest

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# -------------------------------------------------
# GET ALL PENDING TEACHERS
# -------------------------------------------------
@router.get("/pending-teachers")
async def get_pending_teachers(admin: dict = Depends(get_admin_user)):
    """
    Get all teachers whose accounts are pending approval.
    """
    teachers = await db.users.find(
        {"role": "teacher", "is_approved": False},
        {"_id": 0, "password": 0}
    ).to_list(100)

    return teachers


# -------------------------------------------------
# GET ALL TEACHERS (APPROVED + UNAPPROVED)
# -------------------------------------------------
@router.get("/all-teachers")
async def get_all_teachers(admin: dict = Depends(get_admin_user)):
    """
    Get all teachers (approved and unapproved).
    """
    teachers = await db.users.find(
        {"role": "teacher"},
        {"_id": 0, "password": 0}
    ).to_list(200)

    return teachers


# -------------------------------------------------
# APPROVE / DISAPPROVE TEACHER
# -------------------------------------------------
@router.post("/approve-teacher")
async def approve_teacher(
    data: TeacherApprovalRequest,
    admin: dict = Depends(get_admin_user)
):
    """
    Approve or revoke a teacher's account.
    """

    result = await db.users.update_one(
        {"user_id": data.user_id, "role": "teacher"},
        {"$set": {"is_approved": data.approve}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    # -------------------------------------------------
    # CREATE NOTIFICATION
    # -------------------------------------------------
    notification_doc = {
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": data.user_id,
        "message": (
            "Your teacher account has been approved. You can now access the dashboard."
            if data.approve
            else "Your teacher account approval has been revoked."
        ),
        "type": "teacher_approved" if data.approve else "teacher_revoked",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "related_id": None,
    }

    await db.notifications.insert_one(notification_doc)

    return {
        "message": f"Teacher {'approved' if data.approve else 'disapproved'} successfully"
    }
