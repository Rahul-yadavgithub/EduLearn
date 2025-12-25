from fastapi import HTTPException, UploadFile
from datetime import datetime, timezone
import uuid
import base64

from app.core.database import get_db


# -------------------------------------------------
# LIST DOUBTS
# -------------------------------------------------
async def list_doubts(user: dict, status: str | None = None):
    db = get_db()
    query = {}

    if user["role"] == "student":
        query["student_id"] = user["user_id"]

    if status:
        query["status"] = status

    doubts = (
        await db.doubts.find(query, {"_id": 0})
        .sort("created_at", -1)
        .to_list(100)
    )

    return doubts


# -------------------------------------------------
# CREATE DOUBT
# -------------------------------------------------
async def create_doubt(data, user: dict):
    db = get_db()
    if user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Only students can create doubts"
        )

    doubt_id = f"doubt_{uuid.uuid4().hex[:12]}"

    doubt_doc = {
        "doubt_id": doubt_id,
        "student_id": user["user_id"],
        "student_name": user["name"],
        "subject": data.subject,
        "question_text": data.question_text,
        "question_image": data.question_image,
        "status": "pending",
        "answer_text": None,
        "answer_image": None,
        "answered_by": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "answered_at": None,
    }

    await db.doubts.insert_one(doubt_doc)
    return doubt_doc


# -------------------------------------------------
# ANSWER DOUBT
# -------------------------------------------------
async def answer_doubt(doubt_id: str, data, user: dict):
    db = get_db()
    if user["role"] != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Only teachers can answer doubts"
        )

    if not user.get("is_approved", True):
        raise HTTPException(
            status_code=403,
            detail="Your account is pending approval"
        )

    doubt = await db.doubts.find_one({"doubt_id": doubt_id})
    if not doubt:
        raise HTTPException(
            status_code=404,
            detail="Doubt not found"
        )

    update_data = {
        "status": "answered",
        "answer_text": data.answer_text,
        "answer_image": data.answer_image,
        "answered_by": user["user_id"],
        "answered_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.doubts.update_one(
        {"doubt_id": doubt_id},
        {"$set": update_data}
    )

    # Notification
    await db.notifications.insert_one({
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": doubt["student_id"],
        "message": f"Your doubt in {doubt['subject']} has been answered!",
        "type": "doubt_answered",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "related_id": doubt_id,
    })


# -------------------------------------------------
# UPLOAD IMAGE
# -------------------------------------------------
async def upload_doubt_image(image: UploadFile) -> str:
    contents = await image.read()
    encoded = base64.b64encode(contents).decode("utf-8")
    content_type = image.content_type or "image/png"
    return f"data:{content_type};base64,{encoded}"
