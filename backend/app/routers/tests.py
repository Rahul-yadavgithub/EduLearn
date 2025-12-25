from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from app.schemas.test import TestSubmissionSchema
from app.core.security import get_current_user
from app.services.test_service import (
    submit_test,
    get_test_results,
    get_test_result,
)

router = APIRouter(
    prefix="/tests",
    tags=["Tests"]
)

# -------------------------------------------------
# SUBMIT TEST
# -------------------------------------------------
@router.post("/submit")
async def submit_test_route(
    data: TestSubmissionSchema,
    current_user: dict = Depends(get_current_user),
):
    return await submit_test(data, current_user)


# -------------------------------------------------
# GET ALL RESULTS (STUDENT)
# -------------------------------------------------
@router.get("/results", response_model=List[Dict[str, Any]])
async def list_results(current_user: dict = Depends(get_current_user)):
    return await get_test_results(current_user)


# -------------------------------------------------
# GET SINGLE RESULT
# -------------------------------------------------
@router.get("/results/{result_id}")
async def get_result(
    result_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await get_test_result(result_id, current_user)
