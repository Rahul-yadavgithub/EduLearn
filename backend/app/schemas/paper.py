from pydantic import BaseModel
from typing import List, Dict, Any, Optional


# ---------- CREATE ----------
class PaperCreateSchema(BaseModel):
    title: str
    subject: str
    exam_type: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    year: Optional[str] = None
    questions: List[Dict[str, Any]]
    language: str = "English"


# ---------- RESPONSE ----------
class PaperResponse(BaseModel):
    paper_id: str
    title: str
    subject: str
    exam_type: str
    sub_type: Optional[str]
    class_level: Optional[str]
    year: Optional[str]
    questions: List[Dict[str, Any]]
    created_by: str
    created_at: str
    language: str


# ---------- AI ----------
class PaperGenerationRequestSchema(BaseModel):
    num_questions: int
    subject: str
    difficulty: str
    purpose: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    language: str = "English"
    reference_content: Optional[str] = None


class SaveGeneratedPaperSchema(BaseModel):
    title: str
    subject: str
    exam_type: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    year: Optional[str] = None
    questions: List[Dict[str, Any]]
    language: str = "English"
