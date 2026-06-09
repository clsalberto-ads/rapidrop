import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from src.core.database import Base
from src.core.uuid7 import uuid7
import enum


class OnboardingStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    blocked = "blocked"


class MerchantOnboarding(Base):
    __tablename__ = "merchant_onboardings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, unique=True, index=True)
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[OnboardingStatus] = mapped_column(SAEnum(OnboardingStatus), default=OnboardingStatus.pending, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class OnboardingEvent(Base):
    __tablename__ = "onboarding_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    onboarding_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchant_onboardings.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
