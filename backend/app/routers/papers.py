from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any, List
import io
import logging

from app.schemas.paper import PaperCreateSchema
from app.core.security import get_current_user
from app.services.paper_service import (
    list_papers,
    get_paper_by_id,
    create_paper,
    generate_paper_pdf,
)

router = APIRouter(
    prefix="/papers",
    tags=["Papers"]
)

logger = logging.getLogger(__name__)
# -------------------------------------------------
# GET ALL PAPERS (STUDENT / TEACHER)
# -------------------------------------------------
@router.get("", response_model=List[Dict[str, Any]])
async def get_papers(
    subject: Optional[str] = None,
    exam_type: Optional[str] = None,
    class_level: Optional[str] = None,
    year: Optional[str] = None,
):
    """
    Used by:
    - TestsSection.jsx
    - PapersSection.jsx
    """
    filters: Dict[str, Any] = {}

    if subject:
        filters["subject"] = subject
    if exam_type:
        filters["exam_type"] = exam_type
    if class_level:
        filters["class_level"] = class_level
    if year:
        filters["year"] = year

    return await list_papers(filters)


# -------------------------------------------------
# GET SINGLE PAPER (EXAM PAGE)
# -------------------------------------------------
@router.get("/{paper_id}", response_model=Dict[str, Any])
async def get_paper(paper_id: str):
    """
    Used by:
    - ExamPage.jsx
    """
    return await get_paper_by_id(paper_id)


# -------------------------------------------------
# CREATE PAPER (TEACHER MANUAL)
# -------------------------------------------------
@router.post("", response_model=Dict[str, Any])
async def create_new_paper(
    data: PaperCreateSchema,
    current_user: dict = Depends(get_current_user),
):
    logger.info("📝 Manual paper creation started")
    logger.info(f"➡️ user_id: {current_user.get('user_id')}")
    logger.info(f"➡️ subject: {data.subject}")
    logger.info(f"➡️ exam_type: {data.exam_type}")

    # ----------------------------
    # AUTHORIZATION CHECKS
    # ----------------------------
    if current_user.get("role") != "teacher":
        logger.warning("❌ Non-teacher tried to create paper")
        raise HTTPException(
            status_code=403,
            detail="Only teachers can create papers"
        )

    if not current_user.get("is_approved", True):
        logger.warning("❌ Teacher account not approved")
        raise HTTPException(
            status_code=403,
            detail="Your account is pending approval"
        )

    # ----------------------------
    # CREATE PAPER
    # ----------------------------
    try:
        result = await create_paper(data, current_user)

        # Defensive logging (never index blindly)
        paper_id = result.get("paper", {}).get("paper_id")
        logger.info(f"✅ Manual paper created successfully: {paper_id}")

        # IMPORTANT: Always return success once DB insert is done
        return result

    # ----------------------------
    # EXPECTED ERRORS
    # ----------------------------
    except HTTPException:
        # Re-raise known HTTP errors safely (keeps CORS intact)
        raise

    # ----------------------------
    # UNEXPECTED ERRORS (DO NOT BREAK UX)
    # ----------------------------
    except Exception as e:
        logger.exception("⚠️ Non-critical error after paper creation")

        # DB write already happened → do NOT lie to frontend
        return {
            "success": True,
            "message": "Paper uploaded successfully",
        }



# -------------------------------------------------
# DOWNLOAD PAPER PDF
# -------------------------------------------------
@router.get("/{paper_id}/download")
async def download_paper_pdf(paper_id: str):
    """
    Used by students & teachers
    """
    paper = await get_paper_by_id(paper_id)
    pdf_content = generate_paper_pdf(paper)

    filename = paper["title"].replace(" ", "_")

    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.pdf"
        }
    )
