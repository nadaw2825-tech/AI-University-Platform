
from sqlalchemy import select

from backend.app import models
from backend.app.database import SessionLocal
from backend.app.models import User
from backend.app.auth.security import hash_password


def seed_waitlist_student():
    db = SessionLocal()

    try:
        email = "enrollment.student2@example.com"

        student = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if not student:
            student = User(
                full_name="Enrollment Test Student 2",
                email=email,
                password_hash=hash_password("TestPassword123"),
                is_active=True,
                is_verified=True,
            )

            db.add(student)
            db.flush()

        db.commit()

        print("Waitlist test student created successfully.")
        print(f"Student ID: {student.id}")
        print(f"Email: {student.email}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_waitlist_student()



