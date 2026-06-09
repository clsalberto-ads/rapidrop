import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.core.uuid7 import utcnow, uuid7


class SubscriptionStatus(enum.StrEnum):
    trial = "trial"
    active = "active"
    paused = "paused"
    cancelled = "cancelled"
    expired = "expired"


class SubscriptionPhase(enum.StrEnum):
    trial = "trial"
    phase1_percentage = "phase1_percentage"
    phase2_fixed = "phase2_fixed"


class PhaseChangedBy(enum.StrEnum):
    system = "system"
    admin = "admin"
    merchant = "merchant"


class MerchantSubscription(Base):
    __tablename__ = "merchant_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    pricing_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pricing_plans.id"), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(SAEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.trial)
    current_phase: Mapped[SubscriptionPhase] = mapped_column(SAEnum(SubscriptionPhase), nullable=False, default=SubscriptionPhase.trial)
    percentage_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    fixed_monthly_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fixed_monthly_next_review: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trial_orders_count: Mapped[int] = mapped_column(Integer, default=0)
    billing_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payment_gateway: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gateway_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class MerchantSubscriptionPhaseLog(Base):
    __tablename__ = "merchant_subscription_phase_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchant_subscriptions.id"), nullable=False, index=True)
    previous_phase: Mapped[SubscriptionPhase | None] = mapped_column(SAEnum(SubscriptionPhase), nullable=True)
    new_phase: Mapped[SubscriptionPhase] = mapped_column(SAEnum(SubscriptionPhase), nullable=False)
    changed_by: Mapped[PhaseChangedBy] = mapped_column(SAEnum(PhaseChangedBy), nullable=False)
    log_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
