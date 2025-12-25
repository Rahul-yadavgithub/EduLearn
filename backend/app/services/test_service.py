from fastapi import HTTPException
from datetime import datetime, timezone
import uuid

from app.core.database import get_db
from app.utils.mongo import serialize_mongo, serialize_mongo_list


# -------------------------------------------------
# SUBMIT TEST
# -------------------------------------------------
async def submit_test(data, user: dict):
    db = get_db()

    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can submit tests")

    paper = await db.papers.find_one(
        {"paper_id": data.paper_id},
        {"_id": 0}
    )

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    total_questions = len(paper["questions"])
    correct = wrong = unattempted = 0
    subject_wise = {}

    for q in paper["questions"]:
        q_id = q["question_id"]
        subject = q.get("subject", paper["subject"])

        subject_wise.setdefault(subject, {
            "total": 0,
            "correct": 0,
            "wrong": 0
        })

        subject_wise[subject]["total"] += 1
        ans = data.answers.get(q_id)

        if not ans:
            unattempted += 1
        elif ans == q["correct_answer"]:
            correct += 1
            subject_wise[subject]["correct"] += 1
        else:
            wrong += 1
            subject_wise[subject]["wrong"] += 1

    score = (correct * 4) - wrong
    accuracy = round(
        (correct / (correct + wrong) * 100) if (correct + wrong) > 0 else 0,
        2
    )

    result_doc = {
        "result_id": f"result_{uuid.uuid4().hex[:12]}",
        "student_id": user["user_id"],
        "paper_id": data.paper_id,
        "paper_title": paper["title"],
        "exam_type": paper["exam_type"],
        "subject": paper["subject"],
        "total_questions": total_questions,
        "correct_answers": correct,
        "wrong_answers": wrong,
        "unattempted": unattempted,
        "score": score,
        "accuracy": accuracy,
        "time_taken": data.time_taken,
        "subject_wise": subject_wise,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.test_results.insert_one(result_doc)

    # ✅ Safe even if Mongo injects _id later
    return serialize_mongo(result_doc)


# -------------------------------------------------
# GET STUDENT RESULTS
# -------------------------------------------------
async def get_test_results(user: dict):
    db = get_db()

    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view results")

    results = await db.test_results.find(
        {"student_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)

    return serialize_mongo_list(results)


# -------------------------------------------------
# GET SINGLE RESULT
# -------------------------------------------------
async def get_test_result(result_id: str, user: dict):
    db = get_db()

    result = await db.test_results.find_one(
        {"result_id": result_id},
        {"_id": 0}
    )

    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    if user["role"] == "student" and result["student_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return serialize_mongo(result)
