from fastapi import HTTPException
from datetime import datetime, timezone
import uuid, io
from app.core.database import db
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4


async def list_papers(filters: dict):
    return await db.papers.find(filters, {"_id": 0}).to_list(100)


async def get_paper(paper_id: str):
    paper = await db.papers.find_one({"paper_id": paper_id}, {"_id": 0})
    if not paper:
        raise HTTPException(404, "Paper not found")
    return paper


async def create_paper(data, user):
    if user["role"] != "teacher" or not user["is_approved"]:
        raise HTTPException(403)

    paper_id = f"paper_{uuid.uuid4().hex[:12]}"
    doc = data.dict()
    doc.update({
        "paper_id": paper_id,
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    await db.papers.insert_one(doc)
    return doc


def generate_paper_pdf(paper: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title = styles["Heading1"]
    title.alignment = TA_CENTER
    story.append(Paragraph(paper["title"], title))
    story.append(Spacer(1, 12))

    for i, q in enumerate(paper["questions"], 1):
        story.append(Paragraph(f"<b>Q{i}.</b> {q['question_text']}", styles["Normal"]))
        for k, v in q["options"].items():
            story.append(Paragraph(f"({k}) {v}", styles["Normal"]))
        story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
