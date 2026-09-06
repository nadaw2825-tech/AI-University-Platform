import uuid
from datetime import datetime

from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.enrollment.models import (
    AcademicYear,
    Course,
    CourseOffering,
    CoursePrerequisite,
    Department,
    Faculty,
    Semester,
    University,
)
from backend.app.models import User


def seed_enrollment_data():
    db = SessionLocal()

    try:
        # Get existing demo student
        student = db.scalar(
            select(User).where(
                User.email == "nada.demo@example.com"
            )
        )

        if not student:
            print("Demo student not found.")
            return

        # University
        university = db.scalar(
            select(University).where(
                University.code == "AIU"
            )
        )

        if not university:
            university = University(
                name="AI University",
                code="AIU",
            )
            db.add(university)
            db.flush()

        # Faculty
        faculty = db.scalar(
            select(Faculty).where(
                Faculty.code == "FCS",
                Faculty.university_id == university.id,
            )
        )

        if not faculty:
            faculty = Faculty(
                university_id=university.id,
                name="Faculty of Computer Science",
                code="FCS",
            )
            db.add(faculty)
            db.flush()

        # Department
        department = db.scalar(
            select(Department).where(
                Department.code == "CS",
                Department.faculty_id == faculty.id,
            )
        )

        if not department:
            department = Department(
                faculty_id=faculty.id,
                name="Computer Science Department",
                code="CS",
            )
            db.add(department)
            db.flush()

        # Academic Year
        academic_year = db.scalar(
            select(AcademicYear).where(
                AcademicYear.name == "2026-2027"
            )
        )

        if not academic_year:
            academic_year = AcademicYear(
                name="2026-2027",
                start_date=datetime(2026, 9, 1),
                end_date=datetime(2027, 7, 31),
            )
            db.add(academic_year)
            db.flush()

        # Semester
        semester = db.scalar(
            select(Semester).where(
                Semester.name == "Fall 2026",
                Semester.academic_year_id == academic_year.id,
            )
        )

        if not semester:
            semester = Semester(
                academic_year_id=academic_year.id,
                name="Fall 2026",
                start_date=datetime(2026, 9, 1),
                end_date=datetime(2027, 1, 31),
            )
            db.add(semester)
            db.flush()

        # Prerequisite Course
        prerequisite_course = db.scalar(
            select(Course).where(
                Course.code == "CS100"
            )
        )

        if not prerequisite_course:
            prerequisite_course = Course(
                department_id=department.id,
                code="CS100",
                name="Programming Fundamentals",
                description="Basic programming concepts and problem solving.",
                credits=3,
            )
            db.add(prerequisite_course)
            db.flush()

        # Main Course
        course = db.scalar(
            select(Course).where(
                Course.code == "CS101"
            )
        )

        if not course:
            course = Course(
                department_id=department.id,
                code="CS101",
                name="Introduction to Computer Science",
                description="Introduction to computer science concepts.",
                credits=3,
            )
            db.add(course)
            db.flush()

        # Create prerequisite relationship: CS100 -> CS101
        prerequisite = db.scalar(
            select(CoursePrerequisite).where(
                CoursePrerequisite.course_id == course.id,
                CoursePrerequisite.prerequisite_course_id
                == prerequisite_course.id,
            )
        )

        if not prerequisite:
            prerequisite = CoursePrerequisite(
                course_id=course.id,
                prerequisite_course_id=prerequisite_course.id,
            )
            db.add(prerequisite)

        # Course Offering
        offering = db.scalar(
            select(CourseOffering).where(
                CourseOffering.course_id == course.id,
                CourseOffering.semester_id == semester.id,
                CourseOffering.section_name == "Section A",
            )
        )

        if not offering:
            offering = CourseOffering(
                course_id=course.id,
                semester_id=semester.id,
                professor_id=None,
                section_name="Section A",
                capacity=30,
            )
            db.add(offering)
            db.flush()

        db.commit()

        print("Prerequisite test data seeded successfully.")
        print(f"Prerequisite Course: {prerequisite_course.code}")
        print(f"Main Course: {course.code}")
        print("Prerequisite: CS100 -> CS101")
        print(f"Offering ID: {offering.id}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_enrollment_data()