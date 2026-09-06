
from uuid import UUID

from pydantic import BaseModel, Field


class EnrollmentRequest(BaseModel):
    offering_id: UUID


class EnrollmentResponse(BaseModel):
    enrollment_id: UUID
    offering_id: UUID
    status: str
    message: str


class WaitlistResponse(BaseModel):
    waitlist_id: UUID
    offering_id: UUID
    position: int
    status: str
    message: str


class ExceptionRequestCreate(BaseModel):
    offering_id: UUID
    reason: str = Field(min_length=5, max_length=2000)


class ExceptionRequestResponse(BaseModel):
    request_id: UUID
    offering_id: UUID
    status: str
    message: str


class ExceptionRequestReview(BaseModel):
    status: str = Field(pattern="^(APPROVED|REJECTED)$")

