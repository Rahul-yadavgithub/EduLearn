from fastapi import HTTPException
from datetime import datetime, timezone
import uuid, io
from typing import Dict, Any, List

from app.core.database import get_db
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4


# -------------------------------------------------
# LIST PAPERS
# -------------------------------------------------
async def list_papers(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = get_db()
    return await db.papers.find(filters, {"_id": 0}).to_list(100)


# -------------------------------------------------
# GET PAPER BY ID
# -------------------------------------------------
async def get_paper_by_id(paper_id: str) -> Dict[str, Any]:
    db = get_db()
    paper = await db.papers.find_one({"paper_id": paper_id}, {"_id": 0})
    if not paper:
        raise HTTPException(404, "Paper not found")
    return paper


# -------------------------------------------------
# CREATE PAPER
# -------------------------------------------------
async def create_paper(data, user: dict) -> Dict[str, Any]:
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

    db = get_db()
    await db.papers.insert_one(paper_doc)
    return {
        "success": True,
        "message": "Paper uploaded successfully",
        "paper": paper_doc
    }

# -------------------------------------------------
# PDF GENERATION
# -------------------------------------------------
def generate_paper_pdf(paper: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    story.append(Paragraph(paper["title"], title_style))
    story.append(Spacer(1, 12))

    meta = styles["Normal"]
    story.append(Paragraph(f"<b>Subject:</b> {paper['subject']}", meta))
    story.append(Paragraph(f"<b>Exam Type:</b> {paper['exam_type']}", meta))
    if paper.get("year"):
        story.append(Paragraph(f"<b>Year:</b> {paper['year']}", meta))
    story.append(Spacer(1, 24))

    for i, q in enumerate(paper["questions"], start=1):
        story.append(Paragraph(f"<b>Q{i}.</b> {q['question_text']}", meta))
        for key, val in q["options"].items():
            story.append(Paragraph(f"({key}) {val}", meta))
        story.append(Spacer(1, 12))

    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>Answer Key</b>", styles["Heading2"]))
    answers = ", ".join(
        [f"Q{i+1}: {q['correct_answer']}" for i, q in enumerate(paper["questions"])]
    )
    story.append(Paragraph(answers, meta))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
