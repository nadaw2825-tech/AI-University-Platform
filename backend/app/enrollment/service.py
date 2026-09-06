from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.enrollment.models import (
    Course,
    CourseEnrollment,
    CourseOffering,
    CoursePrerequisite,
    CourseWaitlist,
    EnrollmentExceptionRequest,
    SectionSchedule,
    StudentCourseHistory,
)


def enroll_student(
    db: Session,
    student_id: UUID,
    offering_id: UUID,
):
    # 1. Check that the course offering exists
    offering = db.scalar(
        select(CourseOffering).where(
            CourseOffering.id == offering_id,
            CourseOffering.is_active.is_(True),
        )
    )

    if not offering:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course offering not found",
        )

    # 2. Check if the student is already enrolled
    existing_enrollment = db.scalar(
        select(CourseEnrollment).where(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.offering_id == offering_id,
        )
    )

    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already enrolled in this course",
        )

    # 3. Check course prerequisites
    prerequisites = db.scalars(
        select(CoursePrerequisite).where(
            CoursePrerequisite.course_id == offering.course_id
        )
    ).all()

    for prerequisite in prerequisites:
        completed = db.scalar(
            select(StudentCourseHistory).where(
                StudentCourseHistory.student_id == student_id,
                StudentCourseHistory.course_id
                == prerequisite.prerequisite_course_id,
                StudentCourseHistory.passed.is_(True),
            )
        )

        if not completed:
            prerequisite_course = db.scalar(
                select(Course).where(
                    Course.id == prerequisite.prerequisite_course_id
                )
            )

            prerequisite_code = (
                prerequisite_course.code
                if prerequisite_course
                else "Unknown"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Prerequisite not completed: "
                    f"{prerequisite_code}"
                ),
            )

    # 4. Check schedule conflicts
    requested_schedules = db.scalars(
        select(SectionSchedule).where(
            SectionSchedule.offering_id == offering_id
        )
    ).all()

    enrolled_offering_ids = db.scalars(
        select(CourseEnrollment.offering_id).where(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.status == "ENROLLED",
        )
    ).all()

    if requested_schedules and enrolled_offering_ids:
        existing_schedules = db.scalars(
            select(SectionSchedule).where(
                SectionSchedule.offering_id.in_(enrolled_offering_ids)
            )
        ).all()

        for requested in requested_schedules:
            for existing in existing_schedules:
                if requested.day_of_week != existing.day_of_week:
                    continue

                if (
                    requested.start_time < existing.end_time
                    and requested.end_time > existing.start_time
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Schedule conflict with an enrolled course",
                    )

    # 5. Count current enrolled students
    enrolled_count = db.scalar(
        select(func.count(CourseEnrollment.id)).where(
            CourseEnrollment.offering_id == offering_id,
            CourseEnrollment.status == "ENROLLED",
        )
    ) or 0

    # 6. Enroll if seats are available
    if enrolled_count < offering.capacity:
        enrollment = CourseEnrollment(
            student_id=student_id,
            offering_id=offering_id,
            status="ENROLLED",
        )

        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)

        return enrollment

    # 7. Check if the student is already on the waitlist
    existing_waitlist = db.scalar(
        select(CourseWaitlist).where(
            CourseWaitlist.student_id == student_id,
            CourseWaitlist.offering_id == offering_id,
            CourseWaitlist.status == "WAITING",
        )
    )

    if existing_waitlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already on the waitlist for this course",
        )

    # 8. Add student to waitlist
    last_position = db.scalar(
        select(func.max(CourseWaitlist.position)).where(
            CourseWaitlist.offering_id == offering_id
        )
    ) or 0

    waitlist = CourseWaitlist(
        student_id=student_id,
        offering_id=offering_id,
        position=last_position + 1,
        status="WAITING",
    )

    db.add(waitlist)
    db.commit()
    db.refresh(waitlist)

    return waitlist


def create_exception_request(
    db: Session,
    student_id: UUID,
    offering_id: UUID,
    reason: str,
):
    offering = db.scalar(
        select(CourseOffering).where(
            CourseOffering.id == offering_id,
            CourseOffering.is_active.is_(True),
        )
    )

    if not offering:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course offering not found",
        )

    existing_request = db.scalar(
        select(EnrollmentExceptionRequest).where(
            EnrollmentExceptionRequest.student_id == student_id,
            EnrollmentExceptionRequest.offering_id == offering_id,
            EnrollmentExceptionRequest.status == "PENDING",
        )
    )

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already has a pending exception request",
        )

    exception_request = EnrollmentExceptionRequest(
        student_id=student_id,
        offering_id=offering_id,
        reason=reason,
        status="PENDING",
    )

    db.add(exception_request)
    db.commit()
    db.refresh(exception_request)

    return exception_request


def review_exception_request(
    db: Session,
    request_id: UUID,
    reviewer_id: UUID,
    decision: str,
):
    exception_request = db.scalar(
        select(EnrollmentExceptionRequest).where(
            EnrollmentExceptionRequest.id == request_id
        )
    )

    if not exception_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exception request not found",
        )

    if exception_request.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exception request has already been reviewed",
        )

    exception_request.status = decision
    exception_request.reviewed_by = reviewer_id

    from datetime import datetime

    exception_request.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(exception_request)

    return exception_request

