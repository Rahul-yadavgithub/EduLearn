from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

from app.core.database import get_db
from app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.core.security import hash_password

router = APIRouter(tags=["Seed"])


@router.post("/seed")
async def seed_data():
    """
    Seed initial sample data for testing/demo purposes.
    Safe to run multiple times.
    """

    sample_papers = [
        {
            "paper_id": "paper_jee_mains_2024",
            "title": "JEE Mains 2024 - Physics",
            "subject": "Physics",
            "exam_type": "JEE",
            "sub_type": "JEE Mains",
            "class_level": None,
            "year": "2024",
            "language": "English",
            "questions": [
                {
                    "question_id": "q1",
                    "question_text": "A ball is thrown vertically upward with a velocity of 20 m/s. What is the maximum height reached?",
                    "subject": "Physics",
                    "options": {"A": "10 m", "B": "20 m", "C": "40 m", "D": "80 m"},
                    "correct_answer": "B",
                    "explanation": "Using v² = u² − 2gh, at max height v = 0, so h = u² / 2g = 20 m",
                    "difficulty": "Medium",
                },
                {
                    "question_id": "q2",
                    "question_text": "The SI unit of electric field is:",
                    "subject": "Physics",
                    "options": {"A": "N/C", "B": "V/m", "C": "Both A and B", "D": "None"},
                    "correct_answer": "C",
                    "explanation": "N/C and V/m are equivalent units of electric field",
                    "difficulty": "Easy",
                },
            ],
            "created_by": "system",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "paper_id": "paper_neet_2024",
            "title": "NEET 2024 - Biology Mock",
            "subject": "Biology",
            "exam_type": "NEET",
            "sub_type": None,
            "class_level": None,
            "year": "2024",
            "language": "English",
            "questions": [
                {
                    "question_id": "q1",
                    "question_text": "Which organelle is known as the powerhouse of the cell?",
                    "subject": "Biology",
                    "options": {
                        "A": "Nucleus",
                        "B": "Mitochondria",
                        "C": "Ribosome",
                        "D": "Golgi body",
                    },
                    "correct_answer": "B",
                    "explanation": "Mitochondria produce ATP through cellular respiration",
                    "difficulty": "Easy",
                }
            ],
            "created_by": "system",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "paper_id": "paper_school_10_math",
            "title": "Class 10 Mathematics - Chapter Test",
            "subject": "Mathematics",
            "exam_type": "School",
            "sub_type": None,
            "class_level": "10",
            "year": "2024",
            "language": "English",
            "questions": [
                {
                    "question_id": "q1",
                    "question_text": "If the sum of zeros of p(x) = kx² + 2x + 3k is equal to their product, find k.",
                    "subject": "Mathematics",
                    "options": {
                        "A": "1/3",
                        "B": "-1/3",
                        "C": "2/3",
                        "D": "-2/3",
                    },
                    "correct_answer": "C",
                    "explanation": "Using sum = -b/a and product = c/a, solving gives k = -2/3",
                    "difficulty": "Medium",
                }
            ],
            "created_by": "system",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    ]

    inserted_papers = 0
    db = get_db()

    for paper in sample_papers:
        exists = await db.papers.find_one({"paper_id": paper["paper_id"]})
        if not exists:
            await db.papers.insert_one(paper)
            inserted_papers += 1

    # -------------------------------------------------
    # CREATE ADMIN USER IF NOT EXISTS
    # -------------------------------------------------
    admin = await db.users.find_one({"email": ADMIN_EMAIL})
    if not admin:
        admin_doc = {
            "user_id": f"admin_{uuid.uuid4().hex[:12]}",
            "email": ADMIN_EMAIL,
            "name": "Admin",
            "role": "admin",
            "password": hash_password(ADMIN_PASSWORD),
            "picture": None,
            "is_approved": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(admin_doc)

    return {
        "message": "Seed completed successfully",
        "papers_inserted": inserted_papers,
        "admin_created": admin is None,
    }
