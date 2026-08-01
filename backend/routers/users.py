from collections import Counter
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..errors import INVALID_TEST_ANSWERS_RESPONSE, USER_NOT_FOUND_RESPONSE
from ..models import User
from ..schemas import ErrorResponse, TestResultRequest, TestResultResponse


router = APIRouter(prefix="/api/users", tags=["users"])

ALLOWED_ANSWERS = {"perfectionist", "dopamine", "overloaded", "worry"}


@router.post(
    "/type-test",
    response_model=TestResultResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def save_user_type(
    payload: TestResultRequest,
    db: Session = Depends(get_db),
) -> TestResultResponse | JSONResponse:
    answers = payload.answers
    if len(answers) != 4 or any(answer not in ALLOWED_ANSWERS for answer in answers):
        return JSONResponse(status_code=400, content=INVALID_TEST_ANSWERS_RESPONSE)

    counts = Counter(answers)
    user_type = max(answers, key=counts.get)

    if payload.user_id is not None:
        user = db.get(User, payload.user_id)
        if user is None:
            return JSONResponse(status_code=404, content=USER_NOT_FOUND_RESPONSE)
        user.user_type = user_type
    else:
        user = User(id=str(uuid4()), user_type=user_type)
        db.add(user)

    db.commit()
    db.refresh(user)

    return TestResultResponse(
        success=True,
        data={"user_id": user.id, "user_type": user.user_type},
    )
