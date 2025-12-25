from fastapi import HTTPException, UploadFile
from datetime import datetime, timezone
import uuid, base64
from app.core.db import db


async def list_doubts(user, status=None):
    query = {}
    if user["role"] == "student":
        query["student_id"] = user["user_id"]
    if status:
        query["status"] = status
    return await db.doubts.find(query, {"_id": 0}).to_list(100)


async def create_doubt(data, user):
    if user["role"] != "student":
        raise HTTPException(403)

    doubt_id = f"doubt_{uuid.uuid4().hex[:12]}"
    doc = data.dict()
    doc.update({
        "doubt_id": doubt_id,
        "student_id": user["user_id"],
        "student_name": user["name"],
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    await db.doubts.insert_one(doc)
    return doc


async def answer_doubt(doubt_id: str, data, user):
    if user["role"] != "teacher" or not user["is_approved"]:
        raise HTTPException(403)

    doubt = await db.doubts.find_one({"doubt_id": doubt_id})
    if not doubt:
        raise HTTPException(404)

    await db.doubts.update_one(
        {"doubt_id": doubt_id},
        {"$set": {
            "status": "answered",
            **data.dict(exclude_none=True),
            "answered_by": user["user_id"],
            "answered_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    await db.notifications.insert_one({
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": doubt["student_id"],
        "message": f"Your doubt in {doubt['subject']} has been answered!",
        "type": "doubt_answered",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })


async def upload_doubt_image(image: UploadFile):
    data = base64.b64encode(await image.read()).decode()
    return f"data:{image.content_type};base64,{data}"
