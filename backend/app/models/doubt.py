from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ---------- DB MODEL ----------
class Doubt(BaseModel):
    model_config = ConfigDict(extra="ignore")

    doubt_id: str
    student_id: str
    student_name: str
    subject: str
    question_text: str
    question_image: Optional[str] = None
    status: str = "pending"

    answer_text: Optional[str] = None
    answer_image: Optional[str] = None
    answered_by: Optional[str] = None

    created_at: datetime
    answered_at: Optional[datetime] = None


# ---------- CREATE ----------
class DoubtCreate(BaseModel):
    subject: str
    question_text: str
    question_image: Optional[str] = None


# ---------- ANSWER ----------
class DoubtAnswer(BaseModel):
    answer_text: Optional[str] = None
    answer_image: Optional[str] = None
