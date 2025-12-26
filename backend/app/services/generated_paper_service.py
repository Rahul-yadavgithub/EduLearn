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


from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# -------------------------------------------------
# PUBLISH GENERATED PAPER (WITH DEBUG LOGS)
# -------------------------------------------------

async def publish_generated_paper(
    gen_paper_id: str,
    payload: Dict[str, Any],
    user: dict
):
    logger.info("🚀 Publish request started")
    logger.info(f"➡️ gen_paper_id: {gen_paper_id}")
    logger.info(f"➡️ user_id: {user.get('user_id')}")
    logger.info(f"➡️ payload keys: {list(payload.keys())}")

    db = get_db()

    # ---- Fetch generated paper ----
    try:
        gen_paper = await get_generated_paper_by_id(gen_paper_id)
        logger.info("✅ Generated paper fetched from DB")
    except Exception as e:
        logger.error("❌ Failed to fetch generated paper", exc_info=True)
        raise HTTPException(500, "Failed to fetch generated paper")

    if not gen_paper:
        logger.warning("❌ Generated paper NOT FOUND")
        raise HTTPException(404, "Generated paper not found")

    logger.info(f"📄 Generated paper created_by: {gen_paper.get('created_by')}")

    # ---- Ownership check ----
    try:
        if str(gen_paper.get("created_by")) != str(user.get("user_id")):
            logger.warning("❌ Ownership mismatch – access denied")
            raise HTTPException(403, "Access denied")
        logger.info("✅ Ownership verified")
    except Exception:
        logger.error("❌ Error during ownership check", exc_info=True)
        raise

    # ---- Validate required payload fields ----
    required_fields = ["title", "subject", "exam_type", "questions"]
    for field in required_fields:
        if field not in payload:
            logger.error(f"❌ Missing required field in payload: {field}")
            raise HTTPException(400, f"Missing field: {field}")

    logger.info("✅ Payload validation passed")

    # ---- Prepare paper data ----
    try:
        paper_data = {
            "title": payload["title"],
            "subject": payload["subject"],
            "exam_type": payload["exam_type"],
            "sub_type": payload.get("sub_type"),
            "class_level": payload.get("class_level"),
            "year": payload.get("year"),
            "questions": payload["questions"],
            "language": payload.get("language", "English"),
        }
        logger.info("🧾 Paper data prepared successfully")
    except Exception:
        logger.error("❌ Error while preparing paper_data", exc_info=True)
        raise HTTPException(500, "Invalid paper data")

    # ---- Create final paper ----
    try:
        logger.info("🛠️ Calling create_paper()")
        final_paper = await create_paper(paper_data, user)
        logger.info(f"✅ Final paper created with paper_id: {final_paper.get('paper_id')}")
    except Exception:
        logger.error("❌ create_paper() failed", exc_info=True)
        raise HTTPException(500, "Failed to create final paper")

    # ---- Update generated paper status ----
    try:
        await db.generated_papers.update_one(
            {"gen_paper_id": gen_paper_id},
            {"$set": {
                "is_published": True,  # use ONE consistent field
                "published_paper_id": final_paper.get("paper_id"),
                "published_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        logger.info("✅ Generated paper marked as published")
    except Exception:
        logger.error("❌ Failed to update generated paper status", exc_info=True)
        raise HTTPException(500, "Failed to update generated paper")

    logger.info("🎉 Publish flow completed successfully")

    return {
        "message": "Paper published successfully",
        "paper_id": final_paper.get("paper_id")
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
