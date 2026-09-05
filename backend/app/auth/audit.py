from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.models import AuditLog


def create_audit_log(
    db: Session,
    user_id: UUID | None,
    action: str,
    resource_type: str,
    resource_id: UUID | None = None,
    details: str | None = None,
    ip_address: str | None = None
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log