from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Role, User, UserRole


def seed_user_role():
    db = SessionLocal()

    try:
        user = db.scalar(
            select(User).where(
                User.email == "nada.demo@example.com"
            )
        )

        if not user:
            print("Demo user not found.")
            return

        student_role = db.scalar(
            select(Role).where(
                Role.name == "Student"
            )
        )

        if not student_role:
            print("Student role not found.")
            return

        existing_assignment = db.scalar(
            select(UserRole).where(
                UserRole.user_id == user.id,
                UserRole.role_id == student_role.id
            )
        )

        if existing_assignment:
            print("Student role already assigned to demo user.")
            return

        user_role = UserRole(
            user_id=user.id,
            role_id=student_role.id
        )

        db.add(user_role)
        db.commit()

        print("Student role assigned successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_user_role()