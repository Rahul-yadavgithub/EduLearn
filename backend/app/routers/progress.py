from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.services.progress_service import get_student_progress

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("")
async def get_progress(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=403,
            detail="Only students can view progress"
        )

    return await get_student_progress(current_user["user_id"])
