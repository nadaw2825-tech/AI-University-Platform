from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from backend.app.auth.rbac import require_permission
from backend.app.database import get_db
from backend.app.verification.schemas import (
    CertificateCreateRequest,
    CertificateResponse,
    CertificateVerifyResponse,
    DigitalStampCreateRequest,
    DigitalStampResponse,
    QRVerificationMetadataCreateRequest,
    QRVerificationMetadataResponse,
    TranscriptVerificationCreateRequest,
    TranscriptVerificationResponse,
    TranscriptVerifyResponse,
)
from backend.app.verification.service import (
    create_certificate,
    create_digital_stamp,
    create_qr_metadata,
    create_transcript_verification,
    verify_certificate,
    verify_transcript,
)


router = APIRouter(
    prefix="/verification",
    tags=["Digital Verification"],
)


@router.post(
    "/certificates",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_certificate_endpoint(
    request: CertificateCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_digital_verification")
    ),
):
    certificate = create_certificate(
        db=db,
        student_id=request.student_id,
        certificate_number=request.certificate_number,
        certificate_type=request.certificate_type,
        title=request.title,
        issue_date=request.issue_date,
    )

    return CertificateResponse(
        certificate_id=certificate.id,
        student_id=certificate.student_id,
        certificate_number=certificate.certificate_number,
        certificate_type=certificate.certificate_type,
        title=certificate.title,
        issue_date=certificate.issue_date,
        verification_code=certificate.verification_code,
        status=certificate.status,
        created_at=certificate.created_at,
    )


@router.get(
    "/certificates/{verification_code}",
    response_model=CertificateVerifyResponse,
)
def verify_certificate_endpoint(
    verification_code: str,
    db: Session = Depends(get_db),
):
    certificate = verify_certificate(
        db=db,
        verification_code=verification_code,
    )

    if not certificate:
        return CertificateVerifyResponse(
            valid=False,
            certificate_id=None,
            certificate_number=None,
            student_id=None,
            certificate_type=None,
            title=None,
            issue_date=None,
            status=None,
        )

    return CertificateVerifyResponse(
        valid=certificate.status == "VALID",
        certificate_id=certificate.id,
        certificate_number=certificate.certificate_number,
        student_id=certificate.student_id,
        certificate_type=certificate.certificate_type,
        title=certificate.title,
        issue_date=certificate.issue_date,
        status=certificate.status,
    )


@router.post(
    "/transcripts",
    response_model=TranscriptVerificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transcript_verification_endpoint(
    request: TranscriptVerificationCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_digital_verification")
    ),
):
    transcript = create_transcript_verification(
        db=db,
        student_id=request.student_id,
        transcript_hash=request.transcript_hash,
    )

    return TranscriptVerificationResponse(
        verification_id=transcript.id,
        student_id=transcript.student_id,
        verification_code=transcript.verification_code,
        transcript_hash=transcript.transcript_hash,
        status=transcript.status,
        verified_at=transcript.verified_at,
        created_at=transcript.created_at,
    )


@router.get(
    "/transcripts/{verification_code}",
    response_model=TranscriptVerifyResponse,
)
def verify_transcript_endpoint(
    verification_code: str,
    db: Session = Depends(get_db),
):
    transcript = verify_transcript(
        db=db,
        verification_code=verification_code,
    )

    if not transcript:
        return TranscriptVerifyResponse(
            valid=False,
            verification_id=None,
            student_id=None,
            verification_code=None,
            transcript_hash=None,
            status=None,
        )

    return TranscriptVerifyResponse(
        valid=transcript.status == "VALID",
        verification_id=transcript.id,
        student_id=transcript.student_id,
        verification_code=transcript.verification_code,
        transcript_hash=transcript.transcript_hash,
        status=transcript.status,
    )


@router.post(
    "/qr",
    response_model=QRVerificationMetadataResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_qr_metadata_endpoint(
    request: QRVerificationMetadataCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_digital_verification")
    ),
):
    qr_metadata = create_qr_metadata(
        db=db,
        certificate_id=request.certificate_id,
        transcript_verification_id=request.transcript_verification_id,
        verification_url=request.verification_url,
        qr_token=request.qr_token,
    )

    return QRVerificationMetadataResponse(
        qr_metadata_id=qr_metadata.id,
        certificate_id=qr_metadata.certificate_id,
        transcript_verification_id=qr_metadata.transcript_verification_id,
        verification_url=qr_metadata.verification_url,
        qr_token=qr_metadata.qr_token,
        created_at=qr_metadata.created_at,
    )


@router.post(
    "/stamps",
    response_model=DigitalStampResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_digital_stamp_endpoint(
    request: DigitalStampCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_digital_verification")
    ),
):
    digital_stamp = create_digital_stamp(
        db=db,
        certificate_id=request.certificate_id,
        transcript_verification_id=request.transcript_verification_id,
        stamp_code=request.stamp_code,
        issuer_name=request.issuer_name,
        issued_at=request.issued_at,
        stamp_data=request.stamp_data,
    )

    return DigitalStampResponse(
        stamp_id=digital_stamp.id,
        certificate_id=digital_stamp.certificate_id,
        transcript_verification_id=digital_stamp.transcript_verification_id,
        stamp_code=digital_stamp.stamp_code,
        issuer_name=digital_stamp.issuer_name,
        issued_at=digital_stamp.issued_at,
        status=digital_stamp.status,
        stamp_data=digital_stamp.stamp_data,
        created_at=digital_stamp.created_at,
    )