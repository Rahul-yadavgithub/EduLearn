from fastapi import APIRouter
from app.core.database import db
from datetime import datetime, timezone

router = APIRouter(tags=["Seed"])


@router.post("/seed")
async def seed():
    if not await db.papers.find_one({"paper_id": "paper_jee_mains_2024"}):
        await db.papers.insert_one({
            "paper_id": "paper_jee_mains_2024",
            "title": "JEE Mains 2024 Physics",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    return {"message": "Seeded"}
