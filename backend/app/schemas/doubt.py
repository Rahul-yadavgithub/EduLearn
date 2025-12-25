from pydantic import BaseModel
from typing import Optional


# ---------- CREATE ----------
class DoubtCreateSchema(BaseModel):
    subject: str
    question_text: str
    question_image: Optional[str] = None


class DoubtAnswerSchema(BaseModel):
    answer_text: Optional[str] = None
    answer_image: Optional[str] = None


# ---------- RESPONSE ----------
class DoubtResponse(BaseModel):
    doubt_id: str
    student_id: str
    student_name: str
    subject: str
    question_text: str
    question_image: Optional[str]
    status: str
    answer_text: Optional[str]
    answer_image: Optional[str]
    answered_by: Optional[str]
    created_at: str
    answered_at: Optional[str]
