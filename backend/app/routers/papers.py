from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any
import io

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

# -------------------------------------------------
# GET ALL PAPERS
# -------------------------------------------------
@router.get("")
async def get_papers(
    subject: Optional[str] = None,
    exam_type: Optional[str] = None,
    class_level: Optional[str] = None,
    year: Optional[str] = None,
):
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
# GET SINGLE PAPER
# -------------------------------------------------
@router.get("/{paper_id}")
async def get_paper(paper_id: str):
    return await get_paper_by_id(paper_id)


# -------------------------------------------------
# CREATE PAPER
# -------------------------------------------------
@router.post("")
async def create_new_paper(
    data: PaperCreateSchema,
    current_user: dict = Depends(get_current_user),
):
    return await create_paper(data, current_user)


# -------------------------------------------------
# DOWNLOAD PAPER PDF
# -------------------------------------------------
@router.get("/{paper_id}/download")
async def download_paper_pdf(paper_id: str):
    paper = await get_paper_by_id(paper_id)
    pdf_content = generate_paper_pdf(paper)

    filename = paper["title"].replace(" ", "_")

    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.pdf"
        },
    )
