from fastapi import HTTPException, UploadFile
from datetime import datetime, timezone
import json
import uuid
import os
import logging
import base64

from openai import AsyncOpenAI

from app.core.database import get_db

logger = logging.getLogger(__name__)

# ======================================================
# OPENROUTER CONFIG (TEXT + AUDIO)
# ======================================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not configured")

openrouter_client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    default_headers={
        "HTTP-Referer": "https://your-app-domain.com",
        "X-Title": "AI Exam Paper Generator",
    },
)

# ======================================================
# AI PAPER GENERATION (OPENROUTER – GEMINI)
# ======================================================

async def generate_paper_ai(data, current_user: dict):
    db = get_db()

    # ---- Permission checks ----
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can generate papers")

    if not current_user.get("is_approved", True):
        raise HTTPException(status_code=403, detail="Your account is pending approval")

    # ---- Prompt building ----
    exam_context = data.purpose
    if data.sub_type:
        exam_context += f" ({data.sub_type})"
    if data.class_level:
        exam_context += f" for Class {data.class_level}"

    prompt = f"""
Generate {data.num_questions} multiple choice questions for {exam_context} exam.

Subject: {data.subject}
Difficulty: {data.difficulty}
Language: {data.language}

Return ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "question_id": "q1",
      "question_text": "Question text",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Explanation",
      "difficulty": "{data.difficulty}"
    }}
  ]
}}
"""

    try:
        # ---- OpenRouter call (TEXT GENERATION) ----
        response = await openrouter_client.chat.completions.create(
            model="google/gemini-1.5-pro",   # ✅ CORRECT & STABLE
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        raw_text = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error(f"Invalid AI JSON:\n{raw_text}")
            raise HTTPException(status_code=500, detail="AI returned invalid JSON")

        questions = parsed.get("questions", [])
        if not questions:
            raise HTTPException(status_code=500, detail="AI returned empty questions")

        # ---- Normalize question IDs ----
        for i, q in enumerate(questions):
            q.setdefault("question_id", f"q{i+1}")

        gen_paper_id = f"gen_{uuid.uuid4().hex[:12]}"

        # ---- Save to DB ----
        await db.generated_papers.insert_one({
            "gen_paper_id": gen_paper_id,
            "created_by": current_user["user_id"],
            "subject": data.subject,
            "difficulty": data.difficulty,
            "exam_type": data.purpose,
            "sub_type": data.sub_type,
            "class_level": data.class_level,
            "language": data.language,
            "questions": questions,
            "is_published": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

        return {
            "success": True,
            "gen_paper_id": gen_paper_id,
            "questions": questions,
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Paper generation failed: {e}")
        raise HTTPException(status_code=500, detail="Paper generation failed")

# ======================================================
# AUDIO TRANSCRIPTION (OPENROUTER – MULTIMODAL)
# ======================================================

async def transcribe_audio_ai(audio: UploadFile, current_user: dict):
    try:
        audio_bytes = await audio.read()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        response = await openrouter_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Transcribe this audio accurately into English."},
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_b64,
                                "format": "wav"
                            }
                        }
                    ],
                }
            ],
        )

        transcript = response.choices[0].message.content.strip()

        return {
            "success": True,
            "text": transcript
        }

    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        raise HTTPException(status_code=500, detail="Audio transcription failed")
