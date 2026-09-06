
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import get_current_user_id
from backend.app.auth.rbac import require_permission
from backend.app.database import get_db
from backend.app.finance.schemas import (
    FineCreateRequest,
    FinePaymentRequest,
    FineResponse,
    InstallmentCreateRequest,
    InstallmentPaymentRequest,
    InstallmentResponse,
    PaymentCreateRequest,
    PaymentResponse,
    PaymentTransactionCreateRequest,
    PaymentTransactionResponse,
    PaymentWebhookCreateRequest,
    PaymentWebhookResponse,
    ScholarshipCreateRequest,
    ScholarshipResponse,
    TuitionCreateRequest,
    TuitionPaymentRequest,
    TuitionResponse,
    WalletDepositRequest,
    WalletResponse,
    WalletTransactionResponse,
    WalletWithdrawRequest,
)
from backend.app.finance.service import (
    create_fine,
    create_installment,
    create_payment,
    create_payment_transaction,
    create_payment_webhook,
    create_scholarship,
    create_tuition,
    deposit_to_wallet,
    get_fine,
    get_installment,
    get_or_create_wallet,
    get_payment,
    get_payment_transaction,
    get_payment_transactions,
    get_payment_webhook,
    get_payment_webhooks,
    get_scholarship,
    get_student_fines,
    get_student_payments,
    get_student_scholarships,
    get_student_tuitions,
    get_tuition,
    get_tuition_installments,
    get_wallet_transactions,
    update_fine_payment,
    update_installment_payment,
    update_overdue_fines,
    update_overdue_installments,
    update_overdue_tuition,
    update_tuition_payment,
    withdraw_from_wallet,
)


router = APIRouter(
    prefix="/finance",
    tags=["Finance"],
)


@router.get(
    "/wallet",
    response_model=WalletResponse,
)
def get_my_wallet(
    user_id: str = Depends(get_current_user_id),
    _: bool = Depends(
        require_permission("view_wallet")
    ),
    db: Session = Depends(get_db),
):
    wallet = get_or_create_wallet(
        db=db,
        student_id=UUID(user_id),
    )

    return WalletResponse(
        wallet_id=wallet.id,
        student_id=wallet.student_id,
        balance=wallet.balance,
        currency=wallet.currency,
        status=wallet.status,
    )


@router.get(
    "/wallet/transactions",
    response_model=list[WalletTransactionResponse],
)
def get_my_wallet_transactions(
    user_id: str = Depends(get_current_user_id),
    _: bool = Depends(
        require_permission("view_wallet")
    ),
    db: Session = Depends(get_db),
):
    transactions = get_wallet_transactions(
        db=db,
        student_id=UUID(user_id),
    )

    return [
        WalletTransactionResponse(
            transaction_id=transaction.id,
            wallet_id=transaction.wallet_id,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            description=transaction.description,
            reference_type=transaction.reference_type,
            reference_id=transaction.reference_id,
        )
        for transaction in transactions
    ]


@router.post(
    "/wallet/{student_id}/deposit",
    response_model=WalletResponse,
)
def deposit_wallet(
    student_id: UUID,
    request: WalletDepositRequest,
    _: bool = Depends(
        require_permission("manage_wallet")
    ),
    db: Session = Depends(get_db),
):
    wallet = deposit_to_wallet(
        db=db,
        student_id=student_id,
        amount=request.amount,
        description=request.description,
    )

    return WalletResponse(
        wallet_id=wallet.id,
        student_id=wallet.student_id,
        balance=wallet.balance,
        currency=wallet.currency,
        status=wallet.status,
    )


@router.post(
    "/wallet/{student_id}/withdraw",
    response_model=WalletResponse,
)
def withdraw_wallet(
    student_id: UUID,
    request: WalletWithdrawRequest,
    _: bool = Depends(
        require_permission("manage_wallet")
    ),
    db: Session = Depends(get_db),
):
    wallet = withdraw_from_wallet(
        db=db,
        student_id=student_id,
        amount=request.amount,
        description=request.description,
    )

    return WalletResponse(
        wallet_id=wallet.id,
        student_id=wallet.student_id,
        balance=wallet.balance,
        currency=wallet.currency,
        status=wallet.status,
    )


@router.post(
    "/tuition",
    response_model=TuitionResponse,
)
def create_student_tuition(
    request: TuitionCreateRequest,
    _: bool = Depends(
        require_permission("manage_tuition")
    ),
    db: Session = Depends(get_db),
):
    tuition = create_tuition(
        db=db,
        student_id=request.student_id,
        semester_id=request.semester_id,
        total_amount=request.total_amount,
        due_date=request.due_date,
    )

    return TuitionResponse(
        tuition_id=tuition.id,
        student_id=tuition.student_id,
        semester_id=tuition.semester_id,
        total_amount=tuition.total_amount,
        paid_amount=tuition.paid_amount,
        remaining_amount=tuition.remaining_amount,
        due_date=tuition.due_date,
        status=tuition.status,
    )


@router.get(
    "/tuition",
    response_model=TuitionResponse,
)
def get_my_tuition(
    user_id: str = Depends(get_current_user_id),
    _: bool = Depends(
        require_permission("view_tuition")
    ),
    db: Session = Depends(get_db),
):
    tuition = get_tuition(
        db=db,
        student_id=UUID(user_id),
    )

    return TuitionResponse(
        tuition_id=tuition.id,
        student_id=tuition.student_id,
        semester_id=tuition.semester_id,
        total_amount=tuition.total_amount,
        paid_amount=tuition.paid_amount,
        remaining_amount=tuition.remaining_amount,
        due_date=tuition.due_date,
        status=tuition.status,
    )


@router.get(
    "/tuition/all",
    response_model=list[TuitionResponse],
)
def get_my_all_tuitions(
    user_id: str = Depends(get_current_user_id),
    _: bool = Depends(
        require_permission("view_tuition")
    ),
    db: Session = Depends(get_db),
):
    tuitions = get_student_tuitions(
        db=db,
        student_id=UUID(user_id),
    )

    return [
        TuitionResponse(
            tuition_id=tuition.id,
            student_id=tuition.student_id,
            semester_id=tuition.semester_id,
            total_amount=tuition.total_amount,
            paid_amount=tuition.paid_amount,
            remaining_amount=tuition.remaining_amount,
            due_date=tuition.due_date,
            status=tuition.status,
        )
        for tuition in tuitions
    ]


@router.post(
    "/tuition/{tuition_id}/payment",
    response_model=TuitionResponse,
)
def pay_tuition(
    tuition_id: UUID,
    request: TuitionPaymentRequest,
    _: bool = Depends(
        require_permission("manage_tuition")
    ),
    db: Session = Depends(get_db),
):
    tuition = update_tuition_payment(
        db=db,
        tuition_id=tuition_id,
        amount=request.amount,
    )

    return TuitionResponse(
        tuition_id=tuition.id,
        student_id=tuition.student_id,
        semester_id=tuition.semester_id,
        total_amount=tuition.total_amount,
        paid_amount=tuition.paid_amount,
        remaining_amount=tuition.remaining_amount,
        due_date=tuition.due_date,
        status=tuition.status,
    )


@router.post(
    "/tuition/update-overdue",
)
def update_overdue_tuitions(
    _: bool = Depends(
        require_permission("manage_tuition")
    ),
    db: Session = Depends(get_db),
):
    updated_count = update_overdue_tuition(
        db=db,
    )

    return {
        "updated_count": updated_count,
    }


@router.post(
    "/tuition/installments",
    response_model=InstallmentResponse,
)
def create_tuition_installment(
    request: InstallmentCreateRequest,
    _: bool = Depends(
        require_permission("manage_tuition")
    ),
    db: Session = Depends(get_db),
):
    installment = create_installment(
        db=db,
        tuition_id=request.tuition_id,
        installment_number=request.installment_number,
        amount=request.amount,
        due_date=request.due_date,
    )

    return InstallmentResponse(
        installment_id=installment.id,
        tuition_id=installment.tuition_id,
        installment_number=installment.installment_number,
        amount=installment.amount,
        paid_amount=installment.paid_amount,
        remaining_amount=installment.remaining_amount,
        due_date=installment.due_date,
        status=installment.status,
        paid_at=installment.paid_at,
    )


@router.get(
    "/tuition/{tuition_id}/installments",
    response_model=list[InstallmentResponse],
)
def get_installments_for_tuition(
    tuition_id: UUID,
    _: bool = Depends(
        require_permission("view_tuition")
    ),
    db: Session = Depends(get_db),
):
    installments = get_tuition_installments(
        db=db,
        tuition_id=tuition_id,
    )

    return [
        InstallmentResponse(
            installment_id=installment.id,
            tuition_id=installment.tuition_id,
            installment_number=installment.installment_number,
            amount=installment.amount,
            paid_amount=installment.paid_amount,
            remaining_amount=installment.remaining_amount,
            due_date=installment.due_date,
            status=installment.status,
            paid_at=installment.paid_at,
        )
        for installment in installments
    ]


@router.get(
    "/tuition/installments/{installment_id}",
    response_model=InstallmentResponse,
)
def get_single_installment(
    installment_id: UUID,
    _: bool = Depends(
        require_permission("view_tuition")
    ),
    db: Session = Depends(get_db),
):
    installment = get_installment(
        db=db,
        installment_id=installment_id,
    )

    return InstallmentResponse(
        installment_id=installment.id,
        tuition_id=installment.tuition_id,
        installment_number=installment.installment_number,
        amount=installment.amount,
        paid_amount=installment.paid_amount,
        remaining_amount=installment.remaining_amount,
        due_date=installment.due_date,
        status=installment.status,
        paid_at=installment.paid_at,
    )


@router.post(
    "/tuition/installments/{installment_id}/payment",
    response_model=InstallmentResponse,
)
def pay_installment(
    installment_id: UUID,
    request: InstallmentPaymentRequest,
    _: bool = Depends(
        require_permission("manage_tuition")
    ),
    db: Session = Depends(get_db),
):
    installment = update_installment_payment(
        db=db,
        installment_id=installment_id,
        amount=request.amount,
    )

    return InstallmentResponse(
        installment_id=installment.id,
        tuition_id=installment.tuition_id,
        installment_number=installment.installment_number,
        amount=installment.amount,
        paid_amount=installment.paid_amount,
        remaining_amount=installment.remaining_amount,
        due_date=installment.due_date,
        status=installment.status,
        paid_at=installment.paid_at,
    )


@router.post(
    "/tuition/installments/update-overdue",
)
def update_overdue_installments_endpoint(
    _: bool = Depends(
        require_permission("manage_tuition")
    ),
    db: Session = Depends(get_db),
):
    updated_count = update_overdue_installments(
        db=db,
    )

    return {
        "updated_count": updated_count,
    }


@router.post(
    "/fines",
    response_model=FineResponse,
)
def create_student_fine(
    request: FineCreateRequest,
    _: bool = Depends(
        require_permission("manage_fines")
    ),
    db: Session = Depends(get_db),
):
    fine = create_fine(
        db=db,
        student_id=request.student_id,
        amount=request.amount,
        reason=request.reason,
        due_date=request.due_date,
    )

    return FineResponse(
        fine_id=fine.id,
        student_id=fine.student_id,
        amount=fine.amount,
        reason=fine.reason,
        due_date=fine.due_date,
        paid_at=fine.paid_at,
        status=fine.status,
    )


@router.get(
    "/fines",
    response_model=list[FineResponse],
)
def get_my_fines(
    user_id: str = Depends(get_current_user_id),
    _: bool = Depends(
        require_permission("view_fines")
    ),
    db: Session = Depends(get_db),
):
    fines = get_student_fines(
        db=db,
        student_id=UUID(user_id),
    )

    return [
        FineResponse(
            fine_id=fine.id,
            student_id=fine.student_id,
            amount=fine.amount,
            reason=fine.reason,
            due_date=fine.due_date,
            paid_at=fine.paid_at,
            status=fine.status,
        )
        for fine in fines
    ]


@router.get(
    "/fines/{fine_id}",
    response_model=FineResponse,
)
def get_single_fine(
    fine_id: UUID,
    _: bool = Depends(
        require_permission("view_fines")
    ),
    db: Session = Depends(get_db),
):
    fine = get_fine(
        db=db,
        fine_id=fine_id,
    )

    return FineResponse(
        fine_id=fine.id,
        student_id=fine.student_id,
        amount=fine.amount,
        reason=fine.reason,
        due_date=fine.due_date,
        paid_at=fine.paid_at,
        status=fine.status,
    )


@router.post(
    "/fines/{fine_id}/payment",
    response_model=FineResponse,
)
def pay_fine(
    fine_id: UUID,
    request: FinePaymentRequest,
    _: bool = Depends(
        require_permission("manage_fines")
    ),
    db: Session = Depends(get_db),
):
    fine = update_fine_payment(
        db=db,
        fine_id=fine_id,
        amount=request.amount,
    )

    return FineResponse(
        fine_id=fine.id,
        student_id=fine.student_id,
        amount=fine.amount,
        reason=fine.reason,
        due_date=fine.due_date,
        paid_at=fine.paid_at,
        status=fine.status,
    )


@router.post(
    "/fines/update-overdue",
)
def update_overdue_fines_endpoint(
    _: bool = Depends(
        require_permission("manage_fines")
    ),
    db: Session = Depends(get_db),
):
    updated_count = update_overdue_fines(
        db=db,
    )

    return {
        "updated_count": updated_count,
    }


@router.post(
    "/scholarships",
    response_model=ScholarshipResponse,
)
def create_student_scholarship(
    request: ScholarshipCreateRequest,
    _: bool = Depends(
        require_permission("manage_tuition")
    ),
    db: Session = Depends(get_db),
):
    scholarship = create_scholarship(
        db=db,
        student_id=request.student_id,
        tuition_id=request.tuition_id,
        amount=request.amount,
        reason=request.reason,
    )

    return ScholarshipResponse(
        scholarship_id=scholarship.id,
        student_id=scholarship.student_id,
        tuition_id=scholarship.tuition_id,
        amount=scholarship.amount,
        reason=scholarship.reason,
        status=scholarship.status,
        created_at=scholarship.created_at,
    )


@router.get(
    "/scholarships",
    response_model=list[ScholarshipResponse],
)
def get_my_scholarships(
    user_id: str = Depends(get_current_user_id),
    _: bool = Depends(
        require_permission("view_tuition")
    ),
    db: Session = Depends(get_db),
):
    scholarships = get_student_scholarships(
        db=db,
        student_id=UUID(user_id),
    )

    return [
        ScholarshipResponse(
            scholarship_id=scholarship.id,
            student_id=scholarship.student_id,
            tuition_id=scholarship.tuition_id,
            amount=scholarship.amount,
            reason=scholarship.reason,
            status=scholarship.status,
            created_at=scholarship.created_at,
        )
        for scholarship in scholarships
    ]


@router.get(
    "/scholarships/{scholarship_id}",
    response_model=ScholarshipResponse,
)
def get_single_scholarship(
    scholarship_id: UUID,
    _: bool = Depends(
        require_permission("view_tuition")
    ),
    db: Session = Depends(get_db),
):
    scholarship = get_scholarship(
        db=db,
        scholarship_id=scholarship_id,
    )

    return ScholarshipResponse(
        scholarship_id=scholarship.id,
        student_id=scholarship.student_id,
        tuition_id=scholarship.tuition_id,
        amount=scholarship.amount,
        reason=scholarship.reason,
        status=scholarship.status,
        created_at=scholarship.created_at,
    )


@router.post(
    "/payments",
    response_model=PaymentResponse,
)
def create_student_payment(
    request: PaymentCreateRequest,
    _: bool = Depends(
        require_permission("create_payment")
    ),
    db: Session = Depends(get_db),
):
    payment = create_payment(
        db=db,
        student_id=request.student_id,
        amount=request.amount,
        payment_method=request.payment_method,
        tuition_id=request.tuition_id,
        fine_id=request.fine_id,
        installment_id=request.installment_id,
    )

    return PaymentResponse(
        payment_id=payment.id,
        student_id=payment.student_id,
        tuition_id=payment.tuition_id,
        fine_id=payment.fine_id,
        installment_id=payment.installment_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        status=payment.status,
        transaction_reference=payment.transaction_reference,
        created_at=payment.created_at,
    )


@router.get(
    "/payments",
    response_model=list[PaymentResponse],
)
def get_my_payments(
    user_id: str = Depends(get_current_user_id),
    _: bool = Depends(
        require_permission("view_payments")
    ),
    db: Session = Depends(get_db),
):
    payments = get_student_payments(
        db=db,
        student_id=UUID(user_id),
    )

    return [
        PaymentResponse(
            payment_id=payment.id,
            student_id=payment.student_id,
            tuition_id=payment.tuition_id,
            fine_id=payment.fine_id,
            installment_id=payment.installment_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            status=payment.status,
            transaction_reference=payment.transaction_reference,
            created_at=payment.created_at,
        )
        for payment in payments
    ]


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
)
def get_single_payment(
    payment_id: UUID,
    _: bool = Depends(
        require_permission("view_payments")
    ),
    db: Session = Depends(get_db),
):
    payment = get_payment(
        db=db,
        payment_id=payment_id,
    )

    return PaymentResponse(
        payment_id=payment.id,
        student_id=payment.student_id,
        tuition_id=payment.tuition_id,
        fine_id=payment.fine_id,
        installment_id=payment.installment_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        status=payment.status,
        transaction_reference=payment.transaction_reference,
        created_at=payment.created_at,
    )


@router.post(
    "/payment-transactions",
    response_model=PaymentTransactionResponse,
)
def create_transaction(
    request: PaymentTransactionCreateRequest,
    _: bool = Depends(
        require_permission("manage_payment_transactions")
    ),
    db: Session = Depends(get_db),
):
    transaction = create_payment_transaction(
        db=db,
        payment_id=request.payment_id,
        transaction_reference=request.transaction_reference,
        transaction_type=request.transaction_type,
        amount=request.amount,
        gateway_response=request.gateway_response,
    )

    return PaymentTransactionResponse(
        transaction_id=transaction.id,
        payment_id=transaction.payment_id,
        transaction_reference=transaction.transaction_reference,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        status=transaction.status,
        gateway_response=transaction.gateway_response,
        created_at=transaction.created_at,
    )


@router.get(
    "/payment-transactions/{transaction_id}",
    response_model=PaymentTransactionResponse,
)
def get_transaction(
    transaction_id: UUID,
    _: bool = Depends(
        require_permission("manage_payment_transactions")
    ),
    db: Session = Depends(get_db),
):
    transaction = get_payment_transaction(
        db=db,
        transaction_id=transaction_id,
    )

    return PaymentTransactionResponse(
        transaction_id=transaction.id,
        payment_id=transaction.payment_id,
        transaction_reference=transaction.transaction_reference,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        status=transaction.status,
        gateway_response=transaction.gateway_response,
        created_at=transaction.created_at,
    )


@router.get(
    "/payments/{payment_id}/transactions",
    response_model=list[PaymentTransactionResponse],
)
def get_transactions_for_payment(
    payment_id: UUID,
    _: bool = Depends(
        require_permission("manage_payment_transactions")
    ),
    db: Session = Depends(get_db),
):
    transactions = get_payment_transactions(
        db=db,
        payment_id=payment_id,
    )

    return [
        PaymentTransactionResponse(
            transaction_id=transaction.id,
            payment_id=transaction.payment_id,
            transaction_reference=transaction.transaction_reference,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            status=transaction.status,
            gateway_response=transaction.gateway_response,
            created_at=transaction.created_at,
        )
        for transaction in transactions
    ]


@router.post(
    "/payment-webhooks",
    response_model=PaymentWebhookResponse,
)
def create_webhook(
    request: PaymentWebhookCreateRequest,
    _: bool = Depends(
        require_permission("manage_payment_webhooks")
    ),
    db: Session = Depends(get_db),
):
    webhook = create_payment_webhook(
        db=db,
        event_id=request.event_id,
        event_type=request.event_type,
        payload=request.payload,
        payment_id=request.payment_id,
        transaction_id=request.transaction_id,
    )

    return PaymentWebhookResponse(
        webhook_id=webhook.id,
        payment_id=webhook.payment_id,
        transaction_id=webhook.transaction_id,
        event_id=webhook.event_id,
        event_type=webhook.event_type,
        status=webhook.status,
        payload=webhook.payload,
        created_at=webhook.created_at,
        processed_at=webhook.processed_at,
    )


@router.get(
    "/payment-webhooks",
    response_model=list[PaymentWebhookResponse],
)
def get_webhooks(
    _: bool = Depends(
        require_permission("manage_payment_webhooks")
    ),
    db: Session = Depends(get_db),
):
    webhooks = get_payment_webhooks(
        db=db,
    )

    return [
        PaymentWebhookResponse(
            webhook_id=webhook.id,
            payment_id=webhook.payment_id,
            transaction_id=webhook.transaction_id,
            event_id=webhook.event_id,
            event_type=webhook.event_type,
            status=webhook.status,
            payload=webhook.payload,
            created_at=webhook.created_at,
            processed_at=webhook.processed_at,
        )
        for webhook in webhooks
    ]


@router.get(
    "/payment-webhooks/{webhook_id}",
    response_model=PaymentWebhookResponse,
)
def get_single_webhook(
    webhook_id: UUID,
    _: bool = Depends(
        require_permission("manage_payment_webhooks")
    ),
    db: Session = Depends(get_db),
):
    webhook = get_payment_webhook(
        db=db,
        webhook_id=webhook_id,
    )

    return PaymentWebhookResponse(
        webhook_id=webhook.id,
        payment_id=webhook.payment_id,
        transaction_id=webhook.transaction_id,
        event_id=webhook.event_id,
        event_type=webhook.event_type,
        status=webhook.status,
        payload=webhook.payload,
        created_at=webhook.created_at,
        processed_at=webhook.processed_at,
    )




