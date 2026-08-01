from collections import Counter
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import ErrorResponse, TestResultRequest, TestResultResponse


router = APIRouter(prefix="/api", tags=["test-result"])

ALLOWED_ANSWERS = {"perfectionist", "dopamine", "overloaded", "worry"}
INVALID_ANSWERS_RESPONSE = {
    "success": False,
    "error": {
        "code": "INVALID_TEST_ANSWERS",
        "message": "심리테스트 답변을 올바르게 입력해주세요.",
    },
}


@router.post(
    "/test-result",
    response_model=TestResultResponse,
    status_code=201,
    responses={400: {"model": ErrorResponse}},
)
def create_test_result(
    payload: TestResultRequest,
    db: Session = Depends(get_db),
) -> TestResultResponse | JSONResponse:
    answers = payload.answers
    if len(answers) != 4 or any(answer not in ALLOWED_ANSWERS for answer in answers):
        return JSONResponse(status_code=400, content=INVALID_ANSWERS_RESPONSE)

    counts = Counter(answers)
    user_type = max(answers, key=counts.get)
    user = User(id=str(uuid4()), user_type=user_type)

    db.add(user)
    db.commit()
    db.refresh(user)

    return TestResultResponse(
        success=True,
        data={"user_id": user.id, "user_type": user.user_type},
    )
