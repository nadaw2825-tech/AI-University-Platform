
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import get_current_user_id
from backend.app.database import get_db
from backend.app.models import Permission, Role, RolePermission, UserRole


def get_current_user_roles(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> list[str]:
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID"
        )

    roles = db.scalars(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_uuid)
    ).all()

    return [role.name for role in roles]


def get_current_user_permissions(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> list[str]:
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID"
        )

    permissions = db.scalars(
        select(Permission)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id
        )
        .join(
            UserRole,
            UserRole.role_id == RolePermission.role_id
        )
        .where(UserRole.user_id == user_uuid)
    ).all()

    return list({permission.name for permission in permissions})


def require_permission(permission_name: str):
    def permission_checker(
        permissions: list[str] = Depends(get_current_user_permissions)
    ):
        if permission_name not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

        return True

    return permission_checker
