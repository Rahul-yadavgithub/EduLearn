from fastapi import APIRouter, Depends, UploadFile, File
from app.services.ai_service import generate_paper_ai, transcribe_audio_ai
from app.schemas.paper import PaperGenerationRequestSchema
from app.core.security import get_current_user

router = APIRouter()

@router.post("/generate-paper")
async def generate_paper(
    request:  PaperGenerationRequestSchema,
    current_user: dict = Depends(get_current_user)
):
    return await generate_paper_ai(request, current_user)


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    return await transcribe_audio_ai(audio, current_user)
