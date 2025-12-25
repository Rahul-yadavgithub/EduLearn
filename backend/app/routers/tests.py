from fastapi import APIRouter, Depends, HTTPException
from app.schemas.test import TestSubmissionSchema
from app.core.db import db
from app.core.security import get_current_user
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/tests", tags=["Tests"])


@router.post("/submit")
async def submit_test(data: TestSubmissionSchema, user=Depends(get_current_user)):
    if user["role"] != "student":
        raise HTTPException(403)

    paper = await db.papers.find_one({"paper_id": data.paper_id})
    if not paper:
        raise HTTPException(404)

    # SAME scoring logic as original
    correct = wrong = unattempted = 0
    for q in paper["questions"]:
        ans = data.answers.get(q["question_id"])
        if not ans:
            unattempted += 1
        elif ans == q["correct_answer"]:
            correct += 1
        else:
            wrong += 1

    result_id = f"result_{uuid.uuid4().hex[:12]}"
    await db.test_results.insert_one({
        "result_id": result_id,
        "student_id": user["user_id"],
        "paper_id": data.paper_id,
        "score": (correct * 4) - wrong,
        "accuracy": round(correct / max(1, correct + wrong) * 100, 2),
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"result_id": result_id}
