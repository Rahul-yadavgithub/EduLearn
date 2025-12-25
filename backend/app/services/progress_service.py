from app.core.database import get_db

async def get_student_progress(user_id: str):
    db = get_db()

    results = await db.test_results.find(
        {"student_id": user_id},
        {"_id": 0}   # ✅ prevent ObjectId serialization issues
    ).to_list(1000)

    if not results:
        return {
            "total_tests": 0,
            "average_score": 0,
            "average_accuracy": 0,
            "subject_performance": {},
            "recent_results": [],
            "improvement_trend": []
        }

    total_tests = len(results)

    avg_score = sum(r.get("score", 0) for r in results) / total_tests
    avg_accuracy = sum(r.get("accuracy", 0) for r in results) / total_tests

    # ---------------- SUBJECT PERFORMANCE ----------------
    subject_performance = {}

    for r in results:
        for subject, data in r.get("subject_wise", {}).items():
            if subject not in subject_performance:
                subject_performance[subject] = {
                    "total": 0,
                    "correct": 0,
                    "tests": 0
                }

            subject_performance[subject]["total"] += data.get("total", 0)
            subject_performance[subject]["correct"] += data.get("correct", 0)
            subject_performance[subject]["tests"] += 1

    for subject in subject_performance:
        total = subject_performance[subject]["total"]
        correct = subject_performance[subject]["correct"]

        subject_performance[subject]["accuracy"] = (
            round((correct / total) * 100, 2) if total > 0 else 0
        )

    # ---------------- RECENT RESULTS ----------------
    recent_results = sorted(
        results,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )[:10]

    # ---------------- IMPROVEMENT TREND ----------------
    improvement_trend = [
        {
            "date": r.get("created_at"),
            "score": r.get("score", 0),
            "accuracy": r.get("accuracy", 0),
        }
        for r in sorted(results, key=lambda x: x.get("created_at", ""))[-10:]
    ]

    return {
        "total_tests": total_tests,
        "average_score": round(avg_score, 2),
        "average_accuracy": round(avg_accuracy, 2),
        "subject_performance": subject_performance,
        "recent_results": recent_results,
        "improvement_trend": improvement_trend
    }
