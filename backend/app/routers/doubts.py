from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.schemas.doubt import DoubtCreateSchema, DoubtAnswerSchema
from app.core.database import db
from app.core.security import get_current_user
from datetime import datetime, timezone
import uuid, base64

router = APIRouter(prefix="/doubts", tags=["Doubts"])


@router.post("")
async def create_doubt(data: DoubtCreateSchema, user=Depends(get_current_user)):
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


@router.put("/{doubt_id}/answer")
async def answer_doubt(doubt_id: str, data: DoubtAnswerSchema, user=Depends(get_current_user)):
    if user["role"] != "teacher" or not user["is_approved"]:
        raise HTTPException(403)

    await db.doubts.update_one(
        {"doubt_id": doubt_id},
        {"$set": {
            "status": "answered",
            **data.dict(exclude_none=True),
            "answered_by": user["user_id"],
            "answered_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {"message": "Answered"}
