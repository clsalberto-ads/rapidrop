import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Float, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from src.core.database import Base
from src.models.merchant import MerchantSegment


class PricingPlan(Base):
    __tablename__ = "pricing_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    segment: Mapped[MerchantSegment] = mapped_column(SAEnum(MerchantSegment), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    percentage_rate: Mapped[float] = mapped_column(Float, nullable=False)
    trial_months: Mapped[int] = mapped_column(Integer, default=0)
    trial_max_orders: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
