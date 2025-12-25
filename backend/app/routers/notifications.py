from fastapi import APIRouter, Depends
from app.core.db import db
from app.core.security import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(user=Depends(get_current_user)):
    return await db.notifications.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).to_list(50)


@router.put("/{notification_id}/read")
async def mark_read(notification_id: str, user=Depends(get_current_user)):
    await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": user["user_id"]},
        {"$set": {"is_read": True}}
    )
    return {"message": "Read"}
