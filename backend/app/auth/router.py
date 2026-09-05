from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.auth.audit import create_audit_log
from backend.app.auth.dependencies import get_current_user_id
from backend.app.auth.email_verification import (
    generate_verification_token,
    verify_email_token,
)
from backend.app.auth.rbac import require_permission
from backend.app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from backend.app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.app.database import get_db
from backend.app.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    existing_user = db.scalar(
        select(User).where(User.email == request.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    user = User(
        full_name=request.full_name,
        email=request.email,
        password_hash=hash_password(request.password),
        is_active=True,
        is_verified=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    generate_verification_token(
        db=db,
        user=user
    )

    create_audit_log(
        db=db,
        user_id=user.id,
        action="USER_REGISTERED",
        resource_type="USER",
        resource_id=user.id,
        details="New user registered",
        ip_address=http_request.client.host if http_request.client else None
    )

    return UserResponse(
        id=str(user.id),
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        is_verified=user.is_verified
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(User.email == request.email)
    )

    if not user or not verify_password(
        request.password,
        user.password_hash
    ):
        create_audit_log(
            db=db,
            user_id=user.id if user else None,
            action="USER_LOGIN_FAILED",
            resource_type="USER",
            resource_id=user.id if user else None,
            details="Failed login attempt",
            ip_address=http_request.client.host if http_request.client else None
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    create_audit_log(
        db=db,
        user_id=user.id,
        action="USER_LOGIN",
        resource_type="USER",
        resource_id=user.id,
        details="User logged in successfully",
        ip_address=http_request.client.host if http_request.client else None
    )

    access_token = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=str(user.id),
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        is_verified=user.is_verified
    )


@router.get(
    "/verify-email"
)
def verify_email(
    token: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    user = verify_email_token(
        db=db,
        raw_token=token
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or already used verification token"
        )

    create_audit_log(
        db=db,
        user_id=user.id,
        action="USER_EMAIL_VERIFIED",
        resource_type="USER",
        resource_id=user.id,
        details="User email verified successfully",
        ip_address=(
            http_request.client.host
            if http_request.client
            else None
        )
    )

    return {
        "message": "Email verified successfully"
    }


@router.get(
    "/admin-test",
    dependencies=[Depends(require_permission("manage_users"))]
)
def admin_test():
    return {
        "message": "You have admin permission"
    }


@router.get(
    "/student-test",
    dependencies=[Depends(require_permission("view_courses"))]
)
def student_test():
    return {
        "message": "You have permission to view courses"
    }
