import hashlib
import uuid
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.verification.models import (
    Certificate,
    DigitalStamp,
    QRVerificationMetadata,
    TranscriptVerification,
)


def create_certificate(
    db: Session,
    student_id: UUID,
    certificate_number: str,
    certificate_type: str,
    title: str,
    issue_date: datetime,
) -> Certificate:
    certificate_number = certificate_number.strip()
    certificate_type = certificate_type.strip()
    title = title.strip()

    if not certificate_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate number is required",
        )

    if not certificate_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate type is required",
        )

    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate title is required",
        )

    existing_certificate = db.scalar(
        select(Certificate).where(
            Certificate.certificate_number == certificate_number
        )
    )

    if existing_certificate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate number already exists",
        )

    verification_code = f"CERT-{uuid.uuid4().hex.upper()}"

    certificate = Certificate(
        student_id=student_id,
        certificate_number=certificate_number,
        certificate_type=certificate_type,
        title=title,
        issue_date=issue_date,
        verification_code=verification_code,
        status="VALID",
    )

    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    return certificate


def verify_certificate(
    db: Session,
    verification_code: str,
) -> Certificate | None:
    verification_code = verification_code.strip()

    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code is required",
        )

    certificate = db.scalar(
        select(Certificate).where(
            Certificate.verification_code == verification_code
        )
    )

    return certificate


def create_transcript_verification(
    db: Session,
    student_id: UUID,
    transcript_hash: str,
) -> TranscriptVerification:
    transcript_hash = transcript_hash.strip()

    if not transcript_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript hash is required",
        )

    verification_code = f"TRANSCRIPT-{uuid.uuid4().hex.upper()}"

    transcript_verification = TranscriptVerification(
        student_id=student_id,
        verification_code=verification_code,
        transcript_hash=transcript_hash,
        status="VALID",
    )

    db.add(transcript_verification)
    db.commit()
    db.refresh(transcript_verification)

    return transcript_verification


def verify_transcript(
    db: Session,
    verification_code: str,
) -> TranscriptVerification | None:
    verification_code = verification_code.strip()

    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code is required",
        )

    transcript_verification = db.scalar(
        select(TranscriptVerification).where(
            TranscriptVerification.verification_code == verification_code
        )
    )

    if transcript_verification:
        transcript_verification.verified_at = datetime.utcnow()
        db.commit()
        db.refresh(transcript_verification)

    return transcript_verification


def create_qr_metadata(
    db: Session,
    certificate_id: UUID | None,
    transcript_verification_id: UUID | None,
    verification_url: str,
    qr_token: str,
) -> QRVerificationMetadata:
    verification_url = verification_url.strip()
    qr_token = qr_token.strip()

    if certificate_id is None and transcript_verification_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate ID or transcript verification ID is required",
        )

    if certificate_id is not None and transcript_verification_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one verification target can be specified",
        )

    if not verification_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification URL is required",
        )

    if not qr_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="QR token is required",
        )

    existing_qr = db.scalar(
        select(QRVerificationMetadata).where(
            QRVerificationMetadata.qr_token == qr_token
        )
    )

    if existing_qr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="QR token already exists",
        )

    if certificate_id is not None:
        certificate = db.scalar(
            select(Certificate).where(
                Certificate.id == certificate_id
            )
        )

        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found",
            )

    if transcript_verification_id is not None:
        transcript = db.scalar(
            select(TranscriptVerification).where(
                TranscriptVerification.id == transcript_verification_id
            )
        )

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcript verification not found",
            )

    qr_metadata = QRVerificationMetadata(
        certificate_id=certificate_id,
        transcript_verification_id=transcript_verification_id,
        verification_url=verification_url,
        qr_token=qr_token,
    )

    db.add(qr_metadata)
    db.commit()
    db.refresh(qr_metadata)

    return qr_metadata


def create_digital_stamp(
    db: Session,
    certificate_id: UUID | None,
    transcript_verification_id: UUID | None,
    stamp_code: str,
    issuer_name: str,
    issued_at: datetime,
    stamp_data: str | None = None,
) -> DigitalStamp:
    stamp_code = stamp_code.strip()
    issuer_name = issuer_name.strip()

    if certificate_id is None and transcript_verification_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate ID or transcript verification ID is required",
        )

    if certificate_id is not None and transcript_verification_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one verification target can be specified",
        )

    if not stamp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stamp code is required",
        )

    if not issuer_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Issuer name is required",
        )

    existing_stamp = db.scalar(
        select(DigitalStamp).where(
            DigitalStamp.stamp_code == stamp_code
        )
    )

    if existing_stamp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stamp code already exists",
        )

    if certificate_id is not None:
        certificate = db.scalar(
            select(Certificate).where(
                Certificate.id == certificate_id
            )
        )

        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found",
            )

    if transcript_verification_id is not None:
        transcript = db.scalar(
            select(TranscriptVerification).where(
                TranscriptVerification.id == transcript_verification_id
            )
        )

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcript verification not found",
            )

    digital_stamp = DigitalStamp(
        certificate_id=certificate_id,
        transcript_verification_id=transcript_verification_id,
        stamp_code=stamp_code,
        issuer_name=issuer_name,
        issued_at=issued_at,
        status="ACTIVE",
        stamp_data=stamp_data,
    )

    db.add(digital_stamp)
    db.commit()
    db.refresh(digital_stamp)

    return digital_stamp

def generate_transcript_hash(transcript_content: str) -> str:
    transcript_content = transcript_content.strip()

    if not transcript_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript content is required",
        )

    return hashlib.sha256(
        transcript_content.encode("utf-8")
    ).hexdigest()