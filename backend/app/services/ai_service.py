from fastapi import HTTPException, UploadFile
from openai import AsyncOpenAI
from datetime import datetime, timezone
import json
import uuid
import os
import logging

from app.core.database import db

logger = logging.getLogger(__name__)

# ======================================================
# OPENROUTER CONFIG
# ======================================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not configured")

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    default_headers={
        # REQUIRED by OpenRouter
        "HTTP-Referer": "https://your-app-domain.com",  # can be localhost
        "X-Title": "AI Exam Paper Generator"
    }
)

# ======================================================
# AI PAPER GENERATION
# ======================================================

async def generate_paper_ai(data, current_user: dict):
    """
    Fully-featured AI paper generation service (OpenRouter).
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

Rules:
- Exam-quality questions
- One correct answer
- Accurate explanations
- JSON ONLY (no markdown, no text)
"""

    try:
        # ---------- OPENROUTER CHAT COMPLETION ----------
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert educational content creator. "
                        "Always return ONLY valid JSON."
                    )
                },
                {"role": "user", "content": prompt}
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
# VOICE TRANSCRIPTION (IMPORTANT NOTE)
# ======================================================
# ⚠️ OpenRouter DOES NOT support Whisper / Audio APIs.
# You MUST keep OpenAI for transcription OR use another provider.

async def transcribe_audio_ai(
    audio: UploadFile,
    current_user: dict
):
    """
    Whisper transcription MUST still use OpenAI.
    """

    raise HTTPException(
        status_code=501,
        detail="Audio transcription not supported via OpenRouter. Use OpenAI Whisper separately."
    )
