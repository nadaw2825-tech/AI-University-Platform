
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import get_current_user_id
from backend.app.auth.rbac import require_permission
from backend.app.database import get_db
from backend.app.enrollment.schemas import (
    EnrollmentRequest,
    ExceptionRequestCreate,
    ExceptionRequestResponse,
    ExceptionRequestReview,
)
from backend.app.enrollment.service import (
    create_exception_request,
    enroll_student,
    review_exception_request,
)


router = APIRouter(
    prefix="/enrollment",
    tags=["Enrollment"],
)


@router.post("")
def enroll(
    request: EnrollmentRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    student_id = UUID(user_id)

    result = enroll_student(
        db=db,
        student_id=student_id,
        offering_id=request.offering_id,
    )

    if hasattr(result, "position"):
        return {
            "status": "WAITLISTED",
            "waitlist_id": result.id,
            "offering_id": result.offering_id,
            "position": result.position,
            "message": "Course is full. Student added to waitlist.",
        }

    return {
        "status": "ENROLLED",
        "enrollment_id": result.id,
        "offering_id": result.offering_id,
        "message": "Student enrolled successfully.",
    }


@router.post(
    "/exception-request",
    response_model=ExceptionRequestResponse,
)
def create_exception(
    request: ExceptionRequestCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    student_id = UUID(user_id)

    result = create_exception_request(
        db=db,
        student_id=student_id,
        offering_id=request.offering_id,
        reason=request.reason,
    )

    return ExceptionRequestResponse(
        request_id=result.id,
        offering_id=result.offering_id,
        status=result.status,
        message="Exception request submitted successfully.",
    )


@router.post(
    "/exception-request/{request_id}/review",
    response_model=ExceptionRequestResponse,
)
def review_exception(
    request_id: UUID,
    request: ExceptionRequestReview,
    reviewer_id: str = Depends(get_current_user_id),
    _: bool = Depends(
        require_permission("review_exception_requests")
    ),
    db: Session = Depends(get_db),
):
    result = review_exception_request(
        db=db,
        request_id=request_id,
        reviewer_id=UUID(reviewer_id),
        decision=request.status,
    )

    return ExceptionRequestResponse(
        request_id=result.id,
        offering_id=result.offering_id,
        status=result.status,
        message=(
            f"Exception request "
            f"{result.status.lower()} successfully."
        ),
    )








