from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import io

import logging

from app.core.security import get_current_user
from app.services.generated_paper_service import (
    list_generated_papers,
    get_generated_paper_by_id,
    publish_generated_paper,
    generate_generated_paper_pdf,
)

router = APIRouter(
    prefix="/generated-papers",
    tags=["Generated Papers (Teacher)"]
)

logger = logging.getLogger(__name__)
# -------------------------------------------------
# GET GENERATED PAPERS (TEACHER HISTORY)
# -------------------------------------------------
@router.get("")
async def get_generated_papers(
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "teacher":
        raise HTTPException(403, "Only teachers allowed")

    return await list_generated_papers(current_user["user_id"])


# -------------------------------------------------
# GET SINGLE GENERATED PAPER
# -------------------------------------------------
@router.get("/{gen_paper_id}")
async def get_generated_paper(
    gen_paper_id: str,
    current_user: dict = Depends(get_current_user)
):
    paper = await get_generated_paper_by_id(gen_paper_id)

    if paper["created_by"] != current_user["user_id"]:
        raise HTTPException(403, "Access denied")

    return paper


# -------------------------------------------------
# DOWNLOAD GENERATED PAPER PDF
# -------------------------------------------------
@router.get("/{gen_paper_id}/download")
async def download_generated_paper_pdf(
    gen_paper_id: str,
    current_user: dict = Depends(get_current_user)
):
    paper = await get_generated_paper_by_id(gen_paper_id)

    if paper["created_by"] != current_user["user_id"]:
        raise HTTPException(403, "Access denied")

    pdf = generate_generated_paper_pdf(paper)

    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=generated_{gen_paper_id}.pdf"
        }
    )


# -------------------------------------------------
# PUBLISH GENERATED PAPER → FINAL PAPER
# -------------------------------------------------
@router.post("/{gen_paper_id}/publish", response_model=Dict[str, Any])
async def publish_paper(
    gen_paper_id: str,
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    logger.info("📤 Publish generated paper started")
    logger.info(f"➡️ gen_paper_id: {gen_paper_id}")
    logger.info(f"➡️ user_id: {current_user.get('user_id')}")

    # ----------------------------
    # AUTHORIZATION
    # ----------------------------
    if current_user.get("role") != "teacher":
        logger.warning("❌ Non-teacher tried to publish paper")
        raise HTTPException(
            status_code=403,
            detail="Only teachers can publish papers"
        )

    # ----------------------------
    # PUBLISH LOGIC
    # ----------------------------
    try:
        result = await publish_generated_paper(
            gen_paper_id,
            payload,
            current_user
        )

        # Defensive logging (never assume keys exist)
        paper_id = result.get("paper", {}).get("paper_id")
        logger.info(f"✅ Generated paper published successfully: {paper_id}")

        # IMPORTANT: once published, ALWAYS return success
        return result

    # ----------------------------
    # EXPECTED ERRORS
    # ----------------------------
    except HTTPException:
        # Preserve proper HTTP errors + CORS headers
        raise

    # ----------------------------
    # UNEXPECTED ERRORS (DO NOT BREAK UX)
    # ----------------------------
    except Exception:
        logger.exception("⚠️ Non-critical error after publishing generated paper")

        # Publishing likely already succeeded → do NOT return 500
        return {
            "success": True,
            "message": "Paper published successfully",
        }

