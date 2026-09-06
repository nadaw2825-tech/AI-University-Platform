
from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Permission, Role, RolePermission


ROLE_PERMISSIONS = {
    "Student": [
        "view_courses",
        "view_materials",
        "take_quiz",
        "enroll_in_course",
        "view_wallet",
        "view_tuition",
        "view_fines",
        "view_payments",
        "create_payment",
        "view_certificates",
        "verify_transcript",
    ],
    "TA": [
        "view_courses",
        "view_materials",
        "take_quiz",
        "upload_material",
        "create_quiz",
        "manage_enrollment",
        "manage_waitlist",
        "review_exception_requests",
        "view_certificates",
        "verify_transcript",
    ],
    "Professor": [
        "view_courses",
        "view_materials",
        "take_quiz",
        "upload_material",
        "create_quiz",
        "manage_enrollment",
        "manage_waitlist",
        "review_exception_requests",
        "view_wallet",
        "view_tuition",
        "view_fines",
        "view_payments",
        "view_certificates",
        "verify_transcript",
        "manage_certificates",
    ],
    "Admin": [
        "view_courses",
        "view_materials",
        "take_quiz",
        "upload_material",
        "create_quiz",
        "manage_users",
        "approve_role_request",
        "view_audit_logs",
        "manage_roles",
        "manage_permissions",
        "enroll_in_course",
        "manage_enrollment",
        "manage_waitlist",
        "review_exception_requests",
        "view_wallet",
        "manage_wallet",
        "view_tuition",
        "manage_tuition",
        "view_fines",
        "manage_fines",
        "view_payments",
        "create_payment",
        "manage_payment_transactions",
        "manage_payment_webhooks",
        "view_certificates",
        "manage_certificates",
        "verify_transcript",
        "manage_digital_verification",
    ],
}


def seed_role_permissions():
    db = SessionLocal()

    try:
        roles = {
            role.name: role
            for role in db.scalars(select(Role)).all()
        }

        permissions = {
            permission.name: permission
            for permission in db.scalars(select(Permission)).all()
        }

        for role_name, permission_names in ROLE_PERMISSIONS.items():
            role = roles.get(role_name)

            if not role:
                print(f"Role not found: {role_name}")
                continue

            for permission_name in permission_names:
                permission = permissions.get(permission_name)

                if not permission:
                    print(f"Permission not found: {permission_name}")
                    continue

                existing_assignment = db.scalar(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == permission.id
                    )
                )

                if existing_assignment:
                    continue

                role_permission = RolePermission(
                    role_id=role.id,
                    permission_id=permission.id
                )

                db.add(role_permission)

        db.commit()

        print("Role permissions seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_role_permissions()

