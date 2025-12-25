from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any, List
import io

from app.schemas.paper import PaperCreateSchema
from app.core.security import get_current_user
from app.services.paper_service import (
    list_papers,
    get_paper_by_id,
    create_paper,
    generate_paper_pdf,
    publish_generated_paper,
)

router = APIRouter(
    prefix="/generated-papers",
    tags=["Generated Papers"]
)

# -------------------------------------------------
# GET ALL PAPERS (STUDENT / TEACHER)
# -------------------------------------------------
@router.get("")
async def get_papers(
    subject: Optional[str] = None,
    exam_type: Optional[str] = None,
    class_level: Optional[str] = None,
    year: Optional[str] = None,
):
    """
    Public endpoint:
    - Students can see published papers
    - Teachers can see published papers
    """
    query: Dict[str, Any] = {}

    if subject:
        query["subject"] = subject
    if exam_type:
        query["exam_type"] = exam_type
    if class_level:
        query["class_level"] = class_level
    if year:
        query["year"] = year

    return await list_papers(query)


# -------------------------------------------------
# GET SINGLE PAPER (STUDENT / TEACHER)
# -------------------------------------------------
@router.get("/{paper_id}")
async def get_paper(paper_id: str):
    """
    Fetch a single published paper by ID
    """
    paper = await get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


# -------------------------------------------------
# CREATE PAPER (TEACHER ONLY)
# -------------------------------------------------
@router.post("")
async def create_new_paper(
    data: PaperCreateSchema,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a FINAL paper (published for students)

    Used in two cases:
    1. Teacher manually creates a paper
    2. Generated paper is published
    """
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Only teachers can create papers"
        )

    if not current_user.get("is_approved", True):
        raise HTTPException(
            status_code=403,
            detail="Your account is pending approval"
        )

    return await create_paper(data, current_user)


# -------------------------------------------------
# DOWNLOAD PAPER PDF
# -------------------------------------------------
@router.get("/{paper_id}/download")
async def download_paper_pdf(paper_id: str):
    """
    Download a published paper as PDF
    """
    paper = await get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    pdf_content = generate_paper_pdf(paper)

    filename = paper["title"].replace(" ", "_")

    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.pdf"
        },
    )

# -------------------------------------------------
# PUBLISH GENERATED PAPER → FINAL PAPER
# -------------------------------------------------
@router.post("/{gen_paper_id}/publish")
async def publish_paper(
    gen_paper_id: str,
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "teacher":
        raise HTTPException(403, "Only teachers can publish papers")

    return await publish_generated_paper(
        gen_paper_id,
        payload,
        current_user
    )
