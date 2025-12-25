from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime


# ---------- DB MODEL ----------
class Paper(BaseModel):
    model_config = ConfigDict(extra="ignore")

    paper_id: str
    title: str
    subject: str
    exam_type: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    year: Optional[str] = None
    questions: List[Dict[str, Any]]
    created_by: str
    created_at: datetime
    language: str = "English"


# ---------- CREATE ----------
class PaperCreate(BaseModel):
    title: str
    subject: str
    exam_type: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    year: Optional[str] = None
    questions: List[Dict[str, Any]]
    language: str = "English"


# ---------- AI GENERATION ----------
class PaperGenerationRequest(BaseModel):
    num_questions: int
    subject: str
    difficulty: str
    purpose: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    language: str = "English"
    reference_content: Optional[str] = None


class SaveGeneratedPaper(BaseModel):
    title: str
    subject: str
    exam_type: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    year: Optional[str] = None
    questions: List[Dict[str, Any]]
    language: str = "English"
