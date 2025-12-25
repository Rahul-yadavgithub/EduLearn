from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

# -------------------------------------------------
# GET ALL NOTIFICATIONS (LATEST FIRST)
# -------------------------------------------------
@router.get("")
async def list_notifications(current_user: dict = Depends(get_current_user)):
    """
    Get latest notifications for the logged-in user.
    """
    db = get_db()
    notifications = await (
        db.notifications.find(
            {"user_id": current_user["user_id"]},
            {"_id": 0}
        )
        .sort("created_at", -1)
        .to_list(50)
    )

    return notifications


# -------------------------------------------------
# GET UNREAD NOTIFICATION COUNT
# -------------------------------------------------
@router.get("/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    """
    Get count of unread notifications.
    """
    db = get_db()
    count = await db.notifications.count_documents({
        "user_id": current_user["user_id"],
        "is_read": False
    })

    return {"count": count}


# -------------------------------------------------
# MARK SINGLE NOTIFICATION AS READ
# -------------------------------------------------
@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a specific notification as read.
    """
    db = get_db()
    result = await db.notifications.update_one(
        {
            "notification_id": notification_id,
            "user_id": current_user["user_id"]
        },
        {"$set": {"is_read": True}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return {"message": "Notification marked as read"}


# -------------------------------------------------
# MARK ALL NOTIFICATIONS AS READ
# -------------------------------------------------
@router.put("/mark-all-read")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    """
    Mark all notifications as read for the current user.
    """
    db = get_db()
    await db.notifications.update_many(
        {"user_id": current_user["user_id"]},
        {"$set": {"is_read": True}}
    )

    return {"message": "All notifications marked as read"}
