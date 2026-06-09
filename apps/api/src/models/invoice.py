import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.core.uuid7 import uuid7


class InvoiceType(enum.StrEnum):
    percentage = "percentage"
    fixed = "fixed"
    adjustment = "adjustment"


class InvoicePaymentStatus(enum.StrEnum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"


class PaymentTransactionStatus(enum.StrEnum):
    pending = "pending"
    approved = "approved"
    declined = "declined"
    refunded = "refunded"


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchant_subscriptions.id"), nullable=False)
    type: Mapped[InvoiceType] = mapped_column(SAEnum(InvoiceType), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage_amount_cents: Mapped[int] = mapped_column(Integer, default=0)
    fixed_amount_cents: Mapped[int] = mapped_column(Integer, default=0)
    adjustments_cents: Mapped[int] = mapped_column(Integer, default=0)
    payment_status: Mapped[InvoicePaymentStatus] = mapped_column(SAEnum(InvoicePaymentStatus), default=InvoicePaymentStatus.pending, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gateway_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class InvoiceTransaction(Base):
    __tablename__ = "invoice_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    order_amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage_rate: Mapped[float] = mapped_column(nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    gateway: Mapped[str] = mapped_column(String(50), nullable=False)
    gateway_transaction_id: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_cents: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[PaymentTransactionStatus] = mapped_column(SAEnum(PaymentTransactionStatus), default=PaymentTransactionStatus.pending, nullable=False)
    method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
