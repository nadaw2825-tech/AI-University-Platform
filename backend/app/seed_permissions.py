from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Permission


PERMISSIONS = [
    {
        "name": "view_courses",
        "description": "View available courses"
    },
    {
        "name": "view_materials",
        "description": "View course materials"
    },
    {
        "name": "take_quiz",
        "description": "Take quizzes"
    },
    {
        "name": "upload_material",
        "description": "Upload course materials"
    },
    {
        "name": "create_quiz",
        "description": "Create quizzes"
    },
    {
        "name": "manage_users",
        "description": "Manage system users"
    },
    {
        "name": "approve_role_request",
        "description": "Approve or reject role requests"
    },
    {
        "name": "view_audit_logs",
        "description": "View system audit logs"
    },
    {
        "name": "manage_roles",
        "description": "Manage user roles"
    },
    {
        "name": "manage_permissions",
        "description": "Manage system permissions"
    },
    {
        "name": "enroll_in_course",
        "description": "Enroll in courses"
    },
    {
        "name": "manage_enrollment",
        "description": "Manage course enrollment"
    },
    {
        "name": "manage_waitlist",
        "description": "Manage course waitlists"
    },
    {
        "name": "review_exception_requests",
        "description": "Review enrollment exception requests"
    },
    {
        "name": "view_wallet",
        "description": "View student wallet"
    },
    {
        "name": "manage_wallet",
        "description": "Manage student wallet"
    },
    {
        "name": "view_tuition",
        "description": "View tuition information"
    },
    {
        "name": "manage_tuition",
        "description": "Manage tuition records"
    },
    {
        "name": "view_payments",
        "description": "View payment information"
    },
    {
        "name": "create_payment",
        "description": "Create a payment"
    },
    {
        "name": "manage_payment_transactions",
        "description": "Manage payment transactions"
    },
    {
        "name": "manage_payment_webhooks",
        "description": "Process and manage payment webhooks"
    },
    {
        "name": "view_certificates",
        "description": "View certificates"
    },
    {
        "name": "manage_certificates",
        "description": "Manage certificates"
    },
    {
        "name": "verify_transcript",
        "description": "Verify academic transcripts"
    },
    {
        "name": "manage_digital_verification",
        "description": "Manage digital verification records"
    }
]


def seed_permissions():
    db = SessionLocal()

    try:
        for permission_data in PERMISSIONS:
            existing_permission = db.scalar(
                select(Permission).where(
                    Permission.name == permission_data["name"]
                )
            )

            if existing_permission:
                continue

            permission = Permission(
                name=permission_data["name"],
                description=permission_data["description"]
            )

            db.add(permission)

        db.commit()

        print("Permissions seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_permissions()