from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CertificateResponse(BaseModel):
    certificate_id: UUID
    student_id: UUID
    certificate_number: str
    certificate_type: str
    title: str
    issue_date: datetime
    verification_code: str
    status: str
    created_at: datetime


class CertificateCreateRequest(BaseModel):
    student_id: UUID
    certificate_number: str = Field(min_length=1, max_length=100)
    certificate_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    issue_date: datetime


class CertificateVerifyResponse(BaseModel):
    valid: bool
    certificate_id: UUID | None
    certificate_number: str | None
    student_id: UUID | None
    certificate_type: str | None
    title: str | None
    issue_date: datetime | None
    status: str | None


class TranscriptVerificationResponse(BaseModel):
    verification_id: UUID
    student_id: UUID
    verification_code: str
    transcript_hash: str
    status: str
    verified_at: datetime | None
    created_at: datetime


class TranscriptVerificationCreateRequest(BaseModel):
    student_id: UUID
    transcript_hash: str = Field(min_length=1, max_length=255)


class TranscriptVerifyResponse(BaseModel):
    valid: bool
    verification_id: UUID | None
    student_id: UUID | None
    verification_code: str | None
    transcript_hash: str | None
    status: str | None


class QRVerificationMetadataResponse(BaseModel):
    qr_metadata_id: UUID
    certificate_id: UUID | None
    transcript_verification_id: UUID | None
    verification_url: str
    qr_token: str
    created_at: datetime


class QRVerificationMetadataCreateRequest(BaseModel):
    certificate_id: UUID | None = None
    transcript_verification_id: UUID | None = None
    verification_url: str = Field(min_length=1, max_length=1000)
    qr_token: str = Field(min_length=1, max_length=255)


class DigitalStampResponse(BaseModel):
    stamp_id: UUID
    certificate_id: UUID | None
    transcript_verification_id: UUID | None
    stamp_code: str
    issuer_name: str
    issued_at: datetime
    status: str
    stamp_data: str | None
    created_at: datetime


class DigitalStampCreateRequest(BaseModel):
    certificate_id: UUID | None = None
    transcript_verification_id: UUID | None = None
    stamp_code: str = Field(min_length=1, max_length=150)
    issuer_name: str = Field(min_length=1, max_length=255)
    issued_at: datetime
    stamp_data: str | None = Field(default=None, max_length=5000)