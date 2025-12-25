from fastapi import APIRouter, Depends, HTTPException
from app.schemas.paper import PaperCreateSchema
from app.core.db import db
from app.core.security import get_current_user
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/papers", tags=["Papers"])


@router.get("")
async def list_papers():
    return await db.papers.find({}, {"_id": 0}).to_list(100)


@router.post("")
async def create_paper(data: PaperCreateSchema, user=Depends(get_current_user)):
    if user["role"] != "teacher" or not user["is_approved"]:
        raise HTTPException(403, "Teacher access required")

    paper_id = f"paper_{uuid.uuid4().hex[:12]}"
    doc = data.dict()
    doc.update({
        "paper_id": paper_id,
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    await db.papers.insert_one(doc)
    return doc
