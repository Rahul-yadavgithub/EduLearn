from fastapi import HTTPException, UploadFile
from openai import AsyncOpenAI
from datetime import datetime, timezone
import json
import uuid
import os
import logging

from app.core.database import db

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")

if not EMERGENT_LLM_KEY:
    raise RuntimeError("EMERGENT_LLM_KEY is not configured")

client = AsyncOpenAI(api_key=EMERGENT_LLM_KEY)

# ======================================================
# AI PAPER GENERATION
# ======================================================

async def generate_paper_ai(data, current_user: dict):
    """
    Fully-featured AI paper generation service.
    Mirrors router logic EXACTLY but cleaner & reusable.
    """

    # ---------- AUTHORIZATION ----------
    if current_user["role"] != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Only teachers can generate papers"
        )

    if not current_user.get("is_approved", True):
        raise HTTPException(
            status_code=403,
            detail="Your account is pending approval"
        )

    # ---------- CONTEXT BUILDING ----------
    exam_context = data.purpose
    if data.sub_type:
        exam_context += f" ({data.sub_type})"
    if data.class_level:
        exam_context += f" for Class {data.class_level}"

    # ---------- PROMPT ----------
    prompt = f"""
Generate {data.num_questions} multiple choice questions for {exam_context} exam.

Subject: {data.subject}
Difficulty: {data.difficulty}
Language: {data.language}

{f"Reference Content: {data.reference_content}" if data.reference_content else ""}

Return ONLY valid JSON in the following format:
{{
  "questions": [
    {{
      "question_id": "q1",
      "question_text": "Question text here",
      "subject": "{data.subject}",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Brief explanation",
      "difficulty": "{data.difficulty}"
    }}
  ]
}}

Important rules:
- Create exam-quality questions
- Ensure correct answers are accurate
- Provide explanations
- Return ONLY valid JSON
"""

    try:
        # ---------- OPENAI CALL ----------
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert educational content creator. "
                        "Always return ONLY valid JSON. No markdown."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        response_text = response.choices[0].message.content.strip()

        # ---------- JSON SAFETY ----------
        questions_data = json.loads(response_text)
        questions = questions_data.get("questions", [])

        if not questions:
            raise HTTPException(
                status_code=500,
                detail="AI returned empty question list"
            )

        # ---------- ENSURE QUESTION IDs ----------
        for i, q in enumerate(questions):
            q.setdefault("question_id", f"q{i+1}")

        # ---------- DB SAVE ----------
        gen_paper_id = f"gen_{uuid.uuid4().hex[:12]}"

        gen_doc = {
            "gen_paper_id": gen_paper_id,
            "teacher_id": current_user["user_id"],
            "num_questions": len(questions),
            "subject": data.subject,
            "difficulty": data.difficulty,
            "exam_type": data.purpose,
            "sub_type": data.sub_type,
            "class_level": data.class_level,
            "language": data.language,
            "questions": questions,
            "is_published": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        await db.generated_papers.insert_one(gen_doc)

        # ---------- RESPONSE ----------
        return {
            "success": True,
            "gen_paper_id": gen_paper_id,
            "questions": questions,
            "metadata": {
                "num_questions": len(questions),
                "subject": data.subject,
                "difficulty": data.difficulty,
                "exam_type": data.purpose,
                "language": data.language,
            },
        }

    except json.JSONDecodeError as e:
        logger.error(f"AI JSON parse error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to parse AI-generated questions"
        )

    except Exception as e:
        logger.error(f"AI paper generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ======================================================
# VOICE TRANSCRIPTION (WHISPER)
# ======================================================

async def transcribe_audio_ai(
    audio: UploadFile,
    current_user: dict
):
    """
    Robust Whisper transcription service.
    """

    if not EMERGENT_LLM_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )

    try:
        audio_bytes = await audio.read()

        result = await client.audio.transcriptions.create(
            file=(audio.filename or "audio.webm", audio_bytes),
            model="whisper-1",
            language="en",
        )

        return {
            "success": True,
            "text": result.text
        }

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
