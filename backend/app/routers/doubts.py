from fastapi import APIRouter, Depends, UploadFile, File
from typing import Optional

from app.schemas.doubt import (
    DoubtCreateSchema,
    DoubtAnswerSchema,
    DoubtResponse,
)
from app.core.security import get_current_user
from app.services.doubt_service import (
    list_doubts,
    create_doubt,
    answer_doubt,
    upload_doubt_image,
)

router = APIRouter(
    prefix="/doubts",
    tags=["Doubts"]
)

# -------------------------------------------------
# GET DOUBTS
# -------------------------------------------------
@router.get("", response_model=list[DoubtResponse])
async def get_doubts(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    return await list_doubts(current_user, status)


# -------------------------------------------------
# CREATE DOUBT  ✅ FIXED
# -------------------------------------------------
@router.post("", response_model=DoubtResponse)
async def create_doubt_api(
    data: DoubtCreateSchema,
    current_user: dict = Depends(get_current_user),
):
    # ✅ must RETURN the service result
    return await create_doubt(data, current_user)


# -------------------------------------------------
# ANSWER DOUBT
# -------------------------------------------------
@router.put("/{doubt_id}/answer")
async def answer_doubt_api(
    doubt_id: str,
    data: DoubtAnswerSchema,
    current_user: dict = Depends(get_current_user),
):
    await answer_doubt(doubt_id, data, current_user)
    return {"message": "Doubt answered successfully"}


# -------------------------------------------------
# UPLOAD IMAGE
# -------------------------------------------------
@router.post("/upload-image")
async def upload_image_api(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    image_url = await upload_doubt_image(image)
    return {"image_url": image_url}
