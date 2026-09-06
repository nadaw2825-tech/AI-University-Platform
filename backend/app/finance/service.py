
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.finance.models import (
    Fine,
    Installment,
    Payment,
    PaymentTransaction,
    PaymentWebhook,
    Scholarship,
    StudentWallet,
    Tuition,
    WalletTransaction,
)


def get_or_create_wallet(
    db: Session,
    student_id: UUID,
) -> StudentWallet:
    wallet = db.scalar(
        select(StudentWallet).where(
            StudentWallet.student_id == student_id
        )
    )

    if wallet:
        return wallet

    wallet = StudentWallet(
        student_id=student_id,
        balance=Decimal("0.00"),
        currency="EGP",
        status="ACTIVE",
    )

    db.add(wallet)
    db.commit()
    db.refresh(wallet)

    return wallet


def get_wallet(
    db: Session,
    student_id: UUID,
) -> StudentWallet:
    wallet = db.scalar(
        select(StudentWallet).where(
            StudentWallet.student_id == student_id
        )
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student wallet not found",
        )

    return wallet


def deposit_to_wallet(
    db: Session,
    student_id: UUID,
    amount: Decimal,
    description: str | None = None,
) -> StudentWallet:
    wallet = get_or_create_wallet(
        db=db,
        student_id=student_id,
    )

    if wallet.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet is not active",
        )

    wallet.balance += amount

    transaction = WalletTransaction(
        wallet_id=wallet.id,
        transaction_type="DEPOSIT",
        amount=amount,
        description=description,
    )

    db.add(transaction)
    db.commit()
    db.refresh(wallet)

    return wallet


def withdraw_from_wallet(
    db: Session,
    student_id: UUID,
    amount: Decimal,
    description: str | None = None,
) -> StudentWallet:
    wallet = get_wallet(
        db=db,
        student_id=student_id,
    )

    if wallet.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet is not active",
        )

    if wallet.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient wallet balance",
        )

    wallet.balance -= amount

    transaction = WalletTransaction(
        wallet_id=wallet.id,
        transaction_type="WITHDRAWAL",
        amount=amount,
        description=description,
    )

    db.add(transaction)
    db.commit()
    db.refresh(wallet)

    return wallet


def get_wallet_transactions(
    db: Session,
    student_id: UUID,
) -> list[WalletTransaction]:
    wallet = get_wallet(
        db=db,
        student_id=student_id,
    )

    return db.scalars(
        select(WalletTransaction)
        .where(
            WalletTransaction.wallet_id == wallet.id
        )
        .order_by(
            WalletTransaction.created_at.desc()
        )
    ).all()


def create_tuition(
    db: Session,
    student_id: UUID,
    semester_id: UUID,
    total_amount: Decimal,
    due_date: datetime,
) -> Tuition:
    if total_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tuition amount must be greater than zero",
        )

    existing_tuition = db.scalar(
        select(Tuition).where(
            Tuition.student_id == student_id,
            Tuition.semester_id == semester_id,
        )
    )

    if existing_tuition:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tuition record already exists for this student and semester",
        )

    tuition = Tuition(
        student_id=student_id,
        semester_id=semester_id,
        total_amount=total_amount,
        paid_amount=Decimal("0.00"),
        remaining_amount=total_amount,
        due_date=due_date,
        status="PENDING",
    )

    db.add(tuition)
    db.commit()
    db.refresh(tuition)

    return tuition


def get_tuition(
    db: Session,
    student_id: UUID,
    semester_id: UUID | None = None,
) -> Tuition:
    query = select(Tuition).where(
        Tuition.student_id == student_id
    )

    if semester_id:
        query = query.where(
            Tuition.semester_id == semester_id
        )

    tuition = db.scalar(
        query.order_by(
            Tuition.created_at.desc()
        )
    )

    if not tuition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition record not found",
        )

    return tuition


def get_student_tuitions(
    db: Session,
    student_id: UUID,
) -> list[Tuition]:
    return db.scalars(
        select(Tuition)
        .where(
            Tuition.student_id == student_id
        )
        .order_by(
            Tuition.created_at.desc()
        )
    ).all()


def update_tuition_payment(
    db: Session,
    tuition_id: UUID,
    amount: Decimal,
) -> Tuition:
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than zero",
        )

    tuition = db.scalar(
        select(Tuition).where(
            Tuition.id == tuition_id
        )
    )

    if not tuition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition record not found",
        )

    if tuition.status == "PAID":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tuition is already fully paid",
        )

    if amount > tuition.remaining_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount exceeds remaining tuition",
        )

    tuition.paid_amount += amount
    tuition.remaining_amount = (
        tuition.total_amount - tuition.paid_amount
    )

    if tuition.remaining_amount == Decimal("0.00"):
        tuition.status = "PAID"
    else:
        tuition.status = "PARTIALLY_PAID"

    db.commit()
    db.refresh(tuition)

    return tuition


def update_overdue_tuition(
    db: Session,
) -> int:
    now = datetime.utcnow()

    overdue_tuitions = db.scalars(
        select(Tuition).where(
            Tuition.due_date < now,
            Tuition.remaining_amount > Decimal("0.00"),
            Tuition.status.in_(
                ["PENDING", "PARTIALLY_PAID"]
            ),
        )
    ).all()

    for tuition in overdue_tuitions:
        tuition.status = "OVERDUE"

    db.commit()

    return len(overdue_tuitions)


def create_fine(
    db: Session,
    student_id: UUID,
    amount: Decimal,
    reason: str,
    due_date: datetime,
) -> Fine:
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fine amount must be greater than zero",
        )

    fine = Fine(
        student_id=student_id,
        amount=amount,
        reason=reason,
        due_date=due_date,
        paid_at=None,
        status="PENDING",
    )

    db.add(fine)
    db.commit()
    db.refresh(fine)

    return fine


def get_fine(
    db: Session,
    fine_id: UUID,
) -> Fine:
    fine = db.scalar(
        select(Fine).where(
            Fine.id == fine_id
        )
    )

    if not fine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fine not found",
        )

    return fine


def get_student_fines(
    db: Session,
    student_id: UUID,
) -> list[Fine]:
    return db.scalars(
        select(Fine)
        .where(
            Fine.student_id == student_id
        )
        .order_by(
            Fine.created_at.desc()
        )
    ).all()


def update_fine_payment(
    db: Session,
    fine_id: UUID,
    amount: Decimal,
) -> Fine:
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than zero",
        )

    fine = get_fine(
        db=db,
        fine_id=fine_id,
    )

    if fine.status == "PAID":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fine is already fully paid",
        )

    if amount > fine.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount exceeds fine amount",
        )

    if amount < fine.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fine must be paid in full",
        )

    fine.paid_at = datetime.utcnow()
    fine.status = "PAID"

    db.commit()
    db.refresh(fine)

    return fine


def update_overdue_fines(
    db: Session,
) -> int:
    now = datetime.utcnow()

    overdue_fines = db.scalars(
        select(Fine).where(
            Fine.due_date < now,
            Fine.status == "PENDING",
        )
    ).all()

    for fine in overdue_fines:
        fine.status = "OVERDUE"

    db.commit()

    return len(overdue_fines)


def create_installment(
    db: Session,
    tuition_id: UUID,
    installment_number: int,
    amount: Decimal,
    due_date: datetime,
) -> Installment:
    if installment_number <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Installment number must be greater than zero",
        )

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Installment amount must be greater than zero",
        )

    tuition = db.scalar(
        select(Tuition).where(
            Tuition.id == tuition_id
        )
    )

    if not tuition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition record not found",
        )

    existing_installment = db.scalar(
        select(Installment).where(
            Installment.tuition_id == tuition_id,
            Installment.installment_number == installment_number,
        )
    )

    if existing_installment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Installment number already exists for this tuition",
        )

    installments = db.scalars(
        select(Installment).where(
            Installment.tuition_id == tuition_id
        )
    ).all()

    total_installments_amount = sum(
        (
            installment.amount
            for installment in installments
        ),
        Decimal("0.00"),
    )

    if total_installments_amount + amount > tuition.total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total installment amounts cannot exceed tuition amount",
        )

    installment = Installment(
        tuition_id=tuition_id,
        installment_number=installment_number,
        amount=amount,
        paid_amount=Decimal("0.00"),
        remaining_amount=amount,
        due_date=due_date,
        status="PENDING",
        paid_at=None,
    )

    db.add(installment)
    db.commit()
    db.refresh(installment)

    return installment


def get_installment(
    db: Session,
    installment_id: UUID,
) -> Installment:
    installment = db.scalar(
        select(Installment).where(
            Installment.id == installment_id
        )
    )

    if not installment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installment not found",
        )

    return installment


def get_tuition_installments(
    db: Session,
    tuition_id: UUID,
) -> list[Installment]:
    tuition = db.scalar(
        select(Tuition).where(
            Tuition.id == tuition_id
        )
    )

    if not tuition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition record not found",
        )

    return db.scalars(
        select(Installment)
        .where(
            Installment.tuition_id == tuition_id
        )
        .order_by(
            Installment.installment_number.asc()
        )
    ).all()


def update_installment_payment(
    db: Session,
    installment_id: UUID,
    amount: Decimal,
) -> Installment:
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than zero",
        )

    installment = get_installment(
        db=db,
        installment_id=installment_id,
    )

    if installment.status == "PAID":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Installment is already fully paid",
        )

    if amount > installment.remaining_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount exceeds remaining installment",
        )

    installment.paid_amount += amount
    installment.remaining_amount = (
        installment.amount - installment.paid_amount
    )

    if installment.remaining_amount == Decimal("0.00"):
        installment.status = "PAID"
        installment.paid_at = datetime.utcnow()
    else:
        installment.status = "PARTIALLY_PAID"

    db.commit()
    db.refresh(installment)

    return installment


def update_overdue_installments(
    db: Session,
) -> int:
    now = datetime.utcnow()

    overdue_installments = db.scalars(
        select(Installment).where(
            Installment.due_date < now,
            Installment.remaining_amount > Decimal("0.00"),
            Installment.status.in_(
                ["PENDING", "PARTIALLY_PAID"]
            ),
        )
    ).all()

    for installment in overdue_installments:
        installment.status = "OVERDUE"

    db.commit()

    return len(overdue_installments)


def create_scholarship(
    db: Session,
    student_id: UUID,
    tuition_id: UUID,
    amount: Decimal,
    reason: str,
) -> Scholarship:
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scholarship amount must be greater than zero",
        )

    tuition = db.scalar(
        select(Tuition).where(
            Tuition.id == tuition_id
        )
    )

    if not tuition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition record not found",
        )

    if tuition.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tuition does not belong to this student",
        )

    if tuition.status == "PAID":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add scholarship to fully paid tuition",
        )

    if amount > tuition.remaining_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scholarship amount exceeds remaining tuition",
        )

    scholarship = Scholarship(
        student_id=student_id,
        tuition_id=tuition_id,
        amount=amount,
        reason=reason,
        status="ACTIVE",
    )

    tuition.remaining_amount -= amount

    if tuition.remaining_amount == Decimal("0.00"):
        tuition.status = "PAID"

    db.add(scholarship)
    db.commit()
    db.refresh(scholarship)

    return scholarship


def get_scholarship(
    db: Session,
    scholarship_id: UUID,
) -> Scholarship:
    scholarship = db.scalar(
        select(Scholarship).where(
            Scholarship.id == scholarship_id
        )
    )

    if not scholarship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scholarship not found",
        )

    return scholarship


def get_student_scholarships(
    db: Session,
    student_id: UUID,
) -> list[Scholarship]:
    return db.scalars(
        select(Scholarship)
        .where(
            Scholarship.student_id == student_id
        )
        .order_by(
            Scholarship.created_at.desc()
        )
    ).all()


def create_payment(
    db: Session,
    student_id: UUID,
    amount: Decimal,
    payment_method: str,
    tuition_id: UUID | None = None,
    fine_id: UUID | None = None,
    installment_id: UUID | None = None,
) -> Payment:
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than zero",
        )

    target_count = sum(
        target is not None
        for target in (
            tuition_id,
            fine_id,
            installment_id,
        )
    )

    if target_count != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment must be linked to exactly one tuition, fine, or installment",
        )

    if not payment_method.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method is required",
        )

    if tuition_id is not None:
        tuition = db.scalar(
            select(Tuition).where(
                Tuition.id == tuition_id
            )
        )

        if not tuition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tuition record not found",
            )

        if tuition.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tuition does not belong to this student",
            )

        update_tuition_payment(
            db=db,
            tuition_id=tuition_id,
            amount=amount,
        )

    elif fine_id is not None:
        fine = get_fine(
            db=db,
            fine_id=fine_id,
        )

        if fine.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fine does not belong to this student",
            )

        update_fine_payment(
            db=db,
            fine_id=fine_id,
            amount=amount,
        )

    elif installment_id is not None:
        installment = get_installment(
            db=db,
            installment_id=installment_id,
        )

        tuition = db.scalar(
            select(Tuition).where(
                Tuition.id == installment.tuition_id
            )
        )

        if not tuition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tuition record not found",
            )

        if tuition.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Installment does not belong to this student",
            )

        update_installment_payment(
            db=db,
            installment_id=installment_id,
            amount=amount,
        )

    payment = Payment(
        student_id=student_id,
        tuition_id=tuition_id,
        fine_id=fine_id,
        installment_id=installment_id,
        amount=amount,
        payment_method=payment_method.strip(),
        status="COMPLETED",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def get_payment(
    db: Session,
    payment_id: UUID,
) -> Payment:
    payment = db.scalar(
        select(Payment).where(
            Payment.id == payment_id
        )
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


def get_student_payments(
    db: Session,
    student_id: UUID,
) -> list[Payment]:
    return db.scalars(
        select(Payment)
        .where(
            Payment.student_id == student_id
        )
        .order_by(
            Payment.created_at.desc()
        )
    ).all()


def create_payment_transaction(
    db: Session,
    payment_id: UUID,
    transaction_reference: str,
    transaction_type: str,
    amount: Decimal,
    gateway_response: str | None = None,
) -> PaymentTransaction:
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction amount must be greater than zero",
        )

    if not transaction_reference.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction reference is required",
        )

    if not transaction_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction type is required",
        )

    payment = db.scalar(
        select(Payment).where(
            Payment.id == payment_id
        )
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    existing_transaction = db.scalar(
        select(PaymentTransaction).where(
            PaymentTransaction.transaction_reference
            == transaction_reference.strip()
        )
    )

    if existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction reference already exists",
        )

    if amount != payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction amount must match payment amount",
        )

    transaction = PaymentTransaction(
        payment_id=payment_id,
        transaction_reference=transaction_reference.strip(),
        transaction_type=transaction_type.strip(),
        amount=amount,
        status="COMPLETED",
        gateway_response=gateway_response,
    )

    db.add(transaction)

    payment.transaction_reference = transaction_reference.strip()

    db.commit()
    db.refresh(transaction)

    return transaction


def get_payment_transaction(
    db: Session,
    transaction_id: UUID,
) -> PaymentTransaction:
    transaction = db.scalar(
        select(PaymentTransaction).where(
            PaymentTransaction.id == transaction_id
        )
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment transaction not found",
        )

    return transaction


def get_payment_transactions(
    db: Session,
    payment_id: UUID,
) -> list[PaymentTransaction]:
    payment = db.scalar(
        select(Payment).where(
            Payment.id == payment_id
        )
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return db.scalars(
        select(PaymentTransaction)
        .where(
            PaymentTransaction.payment_id == payment_id
        )
        .order_by(
            PaymentTransaction.created_at.desc()
        )
    ).all()


def create_payment_webhook(
    db: Session,
    event_id: str,
    event_type: str,
    payload: str,
    payment_id: UUID | None = None,
    transaction_id: UUID | None = None,
) -> PaymentWebhook:
    if not event_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event ID is required",
        )

    if not event_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event type is required",
        )

    if not payload.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook payload is required",
        )

    existing_webhook = db.scalar(
        select(PaymentWebhook).where(
            PaymentWebhook.event_id == event_id.strip()
        )
    )

    if existing_webhook:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook event has already been processed",
        )

    if payment_id is not None:
        payment = db.scalar(
            select(Payment).where(
                Payment.id == payment_id
            )
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

    if transaction_id is not None:
        transaction = db.scalar(
            select(PaymentTransaction).where(
                PaymentTransaction.id == transaction_id
            )
        )

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment transaction not found",
            )

    if payment_id is not None and transaction_id is not None:
        transaction = db.scalar(
            select(PaymentTransaction).where(
                PaymentTransaction.id == transaction_id
            )
        )

        if transaction and transaction.payment_id != payment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction does not belong to this payment",
            )

    webhook = PaymentWebhook(
        payment_id=payment_id,
        transaction_id=transaction_id,
        event_id=event_id.strip(),
        event_type=event_type.strip(),
        status="PROCESSED",
        payload=payload.strip(),
        processed_at=datetime.utcnow(),
    )

    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return webhook


def get_payment_webhook(
    db: Session,
    webhook_id: UUID,
) -> PaymentWebhook:
    webhook = db.scalar(
        select(PaymentWebhook).where(
            PaymentWebhook.id == webhook_id
        )
    )

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment webhook not found",
        )

    return webhook


def get_payment_webhooks(
    db: Session,
) -> list[PaymentWebhook]:
    return db.scalars(
        select(PaymentWebhook)
        .order_by(
            PaymentWebhook.created_at.desc()
        )
    ).all()


