from pydantic import BaseModel, ConfigDict
from typing import Dict
from datetime import datetime


# ---------- SUBMISSION ----------
class TestSubmission(BaseModel):
    paper_id: str
    answers: Dict[str, str]
    time_taken: int


# ---------- RESULT ----------
class TestResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    result_id: str
    student_id: str
    paper_id: str
    paper_title: str
    exam_type: str
    subject: str

    total_questions: int
    correct_answers: int
    wrong_answers: int
    unattempted: int

    score: float
    accuracy: float
    time_taken: int

    subject_wise: Dict[str, Dict[str, int]]
    created_at: datetime
