import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.core.uuid7 import uuid7


class UnitType(enum.StrEnum):
    unit = "unit"
    kg = "kg"
    g = "g"
    liter = "l"
    ml = "ml"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    unit_type: Mapped[UnitType] = mapped_column(SAEnum(UnitType), default=UnitType.unit, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    has_variations: Mapped[bool] = mapped_column(Boolean, default=False)
    stock_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stock_alert_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    segment_specific: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ProductVariation(Base):
    __tablename__ = "product_variations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_cents_adjustment: Mapped[int] = mapped_column(Integer, default=0)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
