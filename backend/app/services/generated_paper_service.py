from fastapi import HTTPException
from datetime import datetime, timezone
import uuid, io
from typing import Dict, Any, List

from app.core.database import get_db
from app.services.paper_service import create_paper
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4


# -------------------------------------------------
# DB OPERATIONS
# -------------------------------------------------

async def list_generated_papers(user_id: str) -> List[Dict[str, Any]]:
    db = get_db()
    return await db.generated_papers.find(
        {"created_by": user_id},
        {"_id": 0}
    ).to_list(100)


async def get_generated_paper_by_id(gen_paper_id: str) -> Dict[str, Any]:
    db = get_db()
    paper = await db.generated_papers.find_one(
        {"gen_paper_id": gen_paper_id},
        {"_id": 0}
    )
    if not paper:
        raise HTTPException(404, "Generated paper not found")
    return paper


# -------------------------------------------------
# PUBLISH GENERATED PAPER
# -------------------------------------------------

async def publish_generated_paper(
    gen_paper_id: str,
    payload: Dict[str, Any],
    user: dict
):
    db = get_db()
    gen_paper = await get_generated_paper_by_id(gen_paper_id)

    if gen_paper["created_by"] != user["user_id"]:
        raise HTTPException(403, "Access denied")

    paper_data = {
        "title": payload["title"],
        "subject": payload["subject"],
        "exam_type": payload["exam_type"],
        "sub_type": payload.get("sub_type"),
        "class_level": payload.get("class_level"),
        "year": payload.get("year"),
        "questions": payload["questions"],
        "language": payload.get("language"),
    }

    final_paper = await create_paper(paper_data, user)

    await db.generated_papers.update_one(
        {"gen_paper_id": gen_paper_id},
        {"$set": {
            "published": True,
            "published_paper_id": final_paper["paper_id"],
            "published_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {
        "message": "Paper published successfully",
        "paper_id": final_paper["paper_id"]
    }


# -------------------------------------------------
# PDF GENERATION (GENERATED PAPER)
# -------------------------------------------------

def generate_generated_paper_pdf(paper: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title = styles["Heading1"]
    title.alignment = TA_CENTER
    story.append(Paragraph("Generated Question Paper", title))
    story.append(Spacer(1, 12))

    meta = styles["Normal"]
    story.append(Paragraph(f"<b>Subject:</b> {paper['subject']}", meta))
    story.append(Paragraph(f"<b>Difficulty:</b> {paper['difficulty']}", meta))
    story.append(Spacer(1, 24))

    for i, q in enumerate(paper["questions"], 1):
        story.append(Paragraph(f"<b>Q{i}.</b> {q['question_text']}", meta))
        for k, v in q["options"].items():
            story.append(Paragraph(f"({k}) {v}", meta))
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
