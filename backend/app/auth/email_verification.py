
import hashlib
import secrets
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import EmailVerificationToken, User


TOKEN_EXPIRE_MINUTES = 30


def generate_verification_token(
    db: Session,
    user: User
) -> str:
    raw_token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        raw_token.encode()
    ).hexdigest()

    verification_token = EmailVerificationToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(
            minutes=TOKEN_EXPIRE_MINUTES
        )
    )

    db.add(verification_token)
    db.commit()

    return raw_token


def verify_email_token(
    db: Session,
    raw_token: str
) -> User | None:
    token_hash = hashlib.sha256(
        raw_token.encode()
    ).hexdigest()

    verification_token = db.scalar(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash
        )
    )

    if not verification_token:
        return None

    if verification_token.used_at is not None:
        return None

    if verification_token.expires_at < datetime.utcnow():
        return None

    user = db.scalar(
        select(User).where(
            User.id == verification_token.user_id
        )
    )

    if not user:
        return None

    user.is_verified = True
    verification_token.used_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    return user

