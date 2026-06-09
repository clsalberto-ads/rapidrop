import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, JSON, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from src.core.database import Base
import enum


class VehicleType(str, enum.Enum):
    motorcycle = "motorcycle"
    bike = "bike"
    car = "car"


class PaymentMethod(str, enum.Enum):
    per_delivery = "per_delivery"
    per_hour = "per_hour"
    fixed_shift = "fixed_shift"


class PaymentStrategy(str, enum.Enum):
    automatic = "automatic"
    manual = "manual"


class PaymentPeriodStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"


class Rider(Base):
    __tablename__ = "riders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(SAEnum(VehicleType), nullable=False)
    document: Mapped[str] = mapped_column(String(20), nullable=False)
    pix_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    current_location: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RiderPaymentConfig(Base):
    __tablename__ = "rider_payment_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod), nullable=False)
    strategy: Mapped[PaymentStrategy] = mapped_column(SAEnum(PaymentStrategy), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    ranking_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    ranking_config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RiderPaymentPeriod(Base):
    __tablename__ = "rider_payment_periods"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    rider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("riders.id"), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    base_amount_cents: Mapped[int] = mapped_column(Integer, default=0)
    additional_cents: Mapped[int] = mapped_column(Integer, default=0)
    ranking_bonus_cents: Mapped[int] = mapped_column(Integer, default=0)
    total_cents: Mapped[int] = mapped_column(Integer, default=0)
    ranking_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delivery_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[PaymentPeriodStatus] = mapped_column(SAEnum(PaymentPeriodStatus), default=PaymentPeriodStatus.pending, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
