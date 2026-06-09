"""Shared enums used across multiple modules."""

import enum


class RiderStatus(str, enum.Enum):
    available = "available"
    busy = "busy"
    offline = "offline"
    inactive = "inactive"


class VehicleType(str, enum.Enum):
    motorcycle = "motorcycle"
    bicycle = "bicycle"
    car = "car"
    walking = "walking"


class PaymentMethod(str, enum.Enum):
    per_delivery = "per_delivery"
    per_hour = "per_hour"
    monthly_fixed = "monthly_fixed"
    hybrid = "hybrid"


class PaymentStrategy(str, enum.Enum):
    automatic = "automatic"
    manual = "manual"
    ranking_based = "ranking_based"


class PaymentPeriodStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    paid = "paid"
    cancelled = "cancelled"
