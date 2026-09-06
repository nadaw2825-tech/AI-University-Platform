
from datetime import datetime

from decimal import Decimal

from uuid import UUID

from pydantic import BaseModel, Field


class WalletResponse(BaseModel):

    wallet_id: UUID

    student_id: UUID

    balance: Decimal

    currency: str

    status: str


class WalletTransactionResponse(BaseModel):

    transaction_id: UUID

    wallet_id: UUID

    transaction_type: str

    amount: Decimal

    description: str | None

    reference_type: str | None

    reference_id: UUID | None


class WalletDepositRequest(BaseModel):

    amount: Decimal = Field(gt=0)

    description: str | None = Field(default=None, max_length=500)


class WalletWithdrawRequest(BaseModel):

    amount: Decimal = Field(gt=0)

    description: str | None = Field(default=None, max_length=500)


class TuitionResponse(BaseModel):

    tuition_id: UUID

    student_id: UUID

    semester_id: UUID

    total_amount: Decimal

    paid_amount: Decimal

    remaining_amount: Decimal

    due_date: datetime

    status: str


class TuitionCreateRequest(BaseModel):

    student_id: UUID

    semester_id: UUID

    total_amount: Decimal = Field(gt=0)

    due_date: datetime


class TuitionPaymentRequest(BaseModel):

    amount: Decimal = Field(gt=0)


class FineResponse(BaseModel):

    fine_id: UUID

    student_id: UUID

    amount: Decimal

    reason: str

    due_date: datetime

    paid_at: datetime | None

    status: str


class FineCreateRequest(BaseModel):

    student_id: UUID

    amount: Decimal = Field(gt=0)

    reason: str = Field(min_length=1, max_length=500)

    due_date: datetime


class FinePaymentRequest(BaseModel):

    amount: Decimal = Field(gt=0)


class InstallmentResponse(BaseModel):

    installment_id: UUID

    tuition_id: UUID

    installment_number: int

    amount: Decimal

    paid_amount: Decimal

    remaining_amount: Decimal

    due_date: datetime

    status: str

    paid_at: datetime | None


class InstallmentCreateRequest(BaseModel):

    tuition_id: UUID

    installment_number: int = Field(gt=0)

    amount: Decimal = Field(gt=0)

    due_date: datetime


class InstallmentPaymentRequest(BaseModel):

    amount: Decimal = Field(gt=0)


class ScholarshipResponse(BaseModel):

    scholarship_id: UUID

    student_id: UUID

    tuition_id: UUID

    amount: Decimal

    reason: str

    status: str

    created_at: datetime


class ScholarshipCreateRequest(BaseModel):

    student_id: UUID

    tuition_id: UUID

    amount: Decimal = Field(gt=0)

    reason: str = Field(min_length=1, max_length=500)


class PaymentResponse(BaseModel):

    payment_id: UUID

    student_id: UUID

    tuition_id: UUID | None

    fine_id: UUID | None

    installment_id: UUID | None

    amount: Decimal

    payment_method: str

    status: str

    transaction_reference: str | None

    created_at: datetime


class PaymentCreateRequest(BaseModel):

    student_id: UUID

    amount: Decimal = Field(gt=0)

    payment_method: str = Field(
        min_length=1,
        max_length=30
    )

    tuition_id: UUID | None = None

    fine_id: UUID | None = None

    installment_id: UUID | None = None


class PaymentTransactionResponse(BaseModel):

    transaction_id: UUID

    payment_id: UUID

    transaction_reference: str

    transaction_type: str

    amount: Decimal

    status: str

    gateway_response: str | None

    created_at: datetime


class PaymentTransactionCreateRequest(BaseModel):

    payment_id: UUID

    transaction_reference: str = Field(
        min_length=1,
        max_length=100
    )

    transaction_type: str = Field(
        min_length=1,
        max_length=30
    )

    amount: Decimal = Field(gt=0)

    gateway_response: str | None = Field(
        default=None,
        max_length=1000
    )


class PaymentWebhookResponse(BaseModel):

    webhook_id: UUID

    payment_id: UUID | None

    transaction_id: UUID | None

    event_id: str

    event_type: str

    status: str

    payload: str

    created_at: datetime

    processed_at: datetime | None


class PaymentWebhookCreateRequest(BaseModel):

    payment_id: UUID | None = None

    transaction_id: UUID | None = None

    event_id: str = Field(
        min_length=1,
        max_length=100
    )

    event_type: str = Field(
        min_length=1,
        max_length=50
    )

    payload: str = Field(
        min_length=1,
        max_length=5000
    )


