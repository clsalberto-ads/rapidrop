import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.core.uuid7 import uuid7


class OrderChannel(enum.StrEnum):
    whatsapp = "whatsapp"
    app = "app"
    web = "web"
    phone = "phone"


class OrderStatus(enum.StrEnum):
    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    ready = "ready"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class PaymentStatus(enum.StrEnum):
    pending = "pending"
    approved = "approved"
    declined = "declined"
    refunded = "refunded"


class OrderRiderStatus(enum.StrEnum):
    assigned = "assigned"
    accepted = "accepted"
    picked_up = "picked_up"
    delivered = "delivered"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    rider_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("riders.id"), nullable=True)
    sequential_id: Mapped[int] = mapped_column(Integer, nullable=False)
    channel: Mapped[OrderChannel] = mapped_column(SAEnum(OrderChannel), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.pending, nullable=False)
    items: Mapped[dict] = mapped_column(JSON, default=list)
    subtotal_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    delivery_fee_cents: Mapped[int] = mapped_column(Integer, default=0)
    discount_cents: Mapped[int] = mapped_column(Integer, default=0)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    customer_address: Mapped[dict] = mapped_column(JSON, default=dict)
    customer_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    segment_data: Mapped[dict] = mapped_column(JSON, default=dict)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    preparing_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ready_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    out_for_delivery_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_variation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    special_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class OrderRider(Base):
    __tablename__ = "order_riders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    rider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("riders.id"), nullable=False)
    status: Mapped[OrderRiderStatus] = mapped_column(SAEnum(OrderRiderStatus), default=OrderRiderStatus.assigned, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    picked_up_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
