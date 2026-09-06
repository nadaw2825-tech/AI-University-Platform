import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    certificate_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    certificate_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    issue_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    verification_code: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="VALID"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class TranscriptVerification(Base):
    __tablename__ = "transcript_verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    verification_code: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False
    )

    transcript_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="VALID"
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )


class QRVerificationMetadata(Base):
    __tablename__ = "qr_verification_metadata"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    certificate_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("certificates.id"),
        nullable=True
    )

    transcript_verification_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_verifications.id"),
        nullable=True
    )

    verification_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    qr_token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )


class DigitalStamp(Base):
    __tablename__ = "digital_stamps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    certificate_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("certificates.id"),
        nullable=True
    )

    transcript_verification_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_verifications.id"),
        nullable=True
    )

    stamp_code: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False
    )

    issuer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ACTIVE"
    )

    stamp_data: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )