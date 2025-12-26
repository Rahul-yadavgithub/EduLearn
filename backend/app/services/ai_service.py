from fastapi import HTTPException, UploadFile
from datetime import datetime, timezone
import json
import uuid
import os
import logging
import base64

from openai import AsyncOpenAI
import google.generativeai as genai

from app.core.database import get_db

logger = logging.getLogger(__name__)

# ======================================================
# GEMINI CONFIG (PAPER GENERATION)
# ======================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")

genai.configure(api_key=GEMINI_API_KEY)
paper_model = genai.GenerativeModel("gemini-1.5-pro")

# ======================================================
# OPENROUTER CONFIG (AUDIO TRANSCRIPTION)
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
# AI PAPER GENERATION (GEMINI)
# ======================================================

async def generate_paper_ai(data, current_user: dict):
    db = get_db()

    if current_user["role"] != "teacher":
        raise HTTPException(403, "Only teachers can generate papers")

    if not current_user.get("is_approved", True):
        raise HTTPException(403, "Your account is pending approval")

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

{f"Reference Content: {data.reference_content}" if data.reference_content else ""}

Return ONLY valid JSON in this format:
{{
  "questions": [
    {{
      "question_id": "q1",
      "question_text": "Question text",
      "subject": "{data.subject}",
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

Important:
- Create unique, exam-quality questions
- Ensure correct answers are accurate
- Provide clear explanations
- Mix different topics within the subject
- Return ONLY valid JSON, no markdown or extra text
"""

    try:
        response = paper_model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "response_mime_type": "application/json"
            }
        )

        raw_text = response.text.strip()

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error(f"Invalid Gemini JSON:\n{raw_text}")
            raise HTTPException(500, "Gemini returned invalid JSON")

        questions = parsed.get("questions", [])

        if not questions:
            raise HTTPException(500, "Gemini returned empty questions")

        for i, q in enumerate(questions):
            q.setdefault("question_id", f"q{i+1}")

        gen_paper_id = f"gen_{uuid.uuid4().hex[:12]}"

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

    except json.JSONDecodeError:
        raise HTTPException(500, "Gemini returned invalid JSON")

    except Exception as e:
        logger.error(f"Paper generation failed: {e}")
        raise HTTPException(500, str(e))

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
                        {
                            "type": "text",
                            "text": "Transcribe this audio accurately into English."
                        },
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
        logger.error(f"OpenRouter transcription failed: {e}")
        raise HTTPException(500, "Audio transcription failed")
