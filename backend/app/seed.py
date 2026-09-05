from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Role


ROLES = [
    {
        "name": "Student",
        "description": "University student"
    },
    {
        "name": "TA",
        "description": "Teaching assistant"
    },
    {
        "name": "Professor",
        "description": "University professor"
    },
    {
        "name": "Admin",
        "description": "System administrator"
    }
]


def seed_roles():
    db = SessionLocal()

    try:
        for role_data in ROLES:
            existing_role = db.scalar(
                select(Role).where(
                    Role.name == role_data["name"]
                )
            )

            if existing_role:
                continue

            role = Role(
                name=role_data["name"],
                description=role_data["description"]
            )

            db.add(role)

        db.commit()

        print("Roles seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()