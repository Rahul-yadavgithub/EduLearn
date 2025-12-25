from fastapi import HTTPException
from datetime import datetime, timezone
import uuid
from app.core.database import db


async def submit_test(data, user):
    if user["role"] != "student":
        raise HTTPException(403)

    paper = await db.papers.find_one({"paper_id": data.paper_id})
    if not paper:
        raise HTTPException(404)

    correct = wrong = unattempted = 0
    subject_wise = {}

    for q in paper["questions"]:
        sid = q.get("subject", paper["subject"])
        subject_wise.setdefault(sid, {"total": 0, "correct": 0, "wrong": 0})
        subject_wise[sid]["total"] += 1

        ans = data.answers.get(q["question_id"])
        if not ans:
            unattempted += 1
        elif ans == q["correct_answer"]:
            correct += 1
            subject_wise[sid]["correct"] += 1
        else:
            wrong += 1
            subject_wise[sid]["wrong"] += 1

    score = (correct * 4) - wrong
    accuracy = round((correct / max(1, correct + wrong)) * 100, 2)

    result_id = f"result_{uuid.uuid4().hex[:12]}"
    doc = {
        "result_id": result_id,
        "student_id": user["user_id"],
        "paper_id": data.paper_id,
        "paper_title": paper["title"],
        "subject": paper["subject"],
        "score": score,
        "accuracy": accuracy,
        "subject_wise": subject_wise,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.test_results.insert_one(doc)
    return doc


async def get_progress(user):
    results = await db.test_results.find({"student_id": user["user_id"]}).to_list(1000)
    if not results:
        return {"total_tests": 0}
    return results
