from fastapi import HTTPException
from datetime import datetime, timezone
import uuid, io
from typing import Dict, Any, List, Optional

from app.core.database import get_db
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4


# -------------------------------------------------
# DB OPERATIONS
# -------------------------------------------------

async def list_papers(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = get_db()
    return await db.papers.find(filters, {"_id": 0}).to_list(100)


async def get_paper_by_id(paper_id: str) -> Dict[str, Any]:
    db = get_db()
    paper = await db.papers.find_one({"paper_id": paper_id}, {"_id": 0})
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


async def create_paper(data, user: dict) -> Dict[str, Any]:
    db = get_db()
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create papers")

    if not user.get("is_approved", True):
        raise HTTPException(status_code=403, detail="Your account is pending approval")

    paper_id = f"paper_{uuid.uuid4().hex[:12]}"

    paper_doc = {
        "paper_id": paper_id,
        "title": data.title,
        "subject": data.subject,
        "exam_type": data.exam_type,
        "sub_type": data.sub_type,
        "class_level": data.class_level,
        "year": data.year,
        "questions": data.questions,
        "language": data.language,
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.papers.insert_one(paper_doc)
    return paper_doc


# -------------------------------------------------
# PUBLISH GENERATED PAPER
# -------------------------------------------------

async def publish_generated_paper(
    gen_paper_id: str,
    payload: Dict[str, Any],
    user: dict
):
    db = get_db()
    gen_paper = await get_paper_by_id(gen_paper_id)

    if gen_paper["created_by"] != user["user_id"]:
        raise HTTPException(403, "Access denied")

    final_data = {
        "title": payload["title"],
        "subject": payload["subject"],
        "exam_type": payload["exam_type"],
        "sub_type": payload.get("sub_type"),
        "class_level": payload.get("class_level"),
        "year": payload.get("year"),
        "questions": payload["questions"],
        "language": payload.get("language"),
    }

    final_paper = await create_paper(final_data, user)

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
# PDF GENERATION
# -------------------------------------------------

def generate_paper_pdf(paper: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    story.append(Paragraph(paper["title"], title_style))
    story.append(Spacer(1, 12))

    # Metadata
    meta = styles["Normal"]
    story.append(Paragraph(f"<b>Subject:</b> {paper['subject']}", meta))
    story.append(Paragraph(f"<b>Exam Type:</b> {paper['exam_type']}", meta))
    if paper.get("year"):
        story.append(Paragraph(f"<b>Year:</b> {paper['year']}", meta))
    story.append(Spacer(1, 24))

    # Questions
    for i, q in enumerate(paper["questions"], start=1):
        story.append(Paragraph(f"<b>Q{i}.</b> {q['question_text']}", meta))
        story.append(Spacer(1, 6))
        for key, val in q["options"].items():
            story.append(Paragraph(f"({key}) {val}", meta))
        story.append(Spacer(1, 12))

    # Answer Key
    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>Answer Key</b>", styles["Heading2"]))
    story.append(Spacer(1, 12))

    answers = ", ".join(
        [f"Q{i+1}: {q['correct_answer']}" for i, q in enumerate(paper["questions"])]
    )
    story.append(Paragraph(answers, meta))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
