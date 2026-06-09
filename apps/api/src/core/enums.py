"""Shared enums used across multiple modules."""

import enum


class RiderStatus(enum.StrEnum):
    available = "available"
    busy = "busy"
    offline = "offline"
    inactive = "inactive"


class VehicleType(enum.StrEnum):
    motorcycle = "motorcycle"
    bicycle = "bicycle"
    car = "car"
    walking = "walking"


class PaymentMethod(enum.StrEnum):
    per_delivery = "per_delivery"
    per_hour = "per_hour"
    monthly_fixed = "monthly_fixed"
    hybrid = "hybrid"


class PaymentStrategy(enum.StrEnum):
    automatic = "automatic"
    manual = "manual"
    ranking_based = "ranking_based"


class PaymentPeriodStatus(enum.StrEnum):
    pending = "pending"
    approved = "approved"
    paid = "paid"
    cancelled = "cancelled"
