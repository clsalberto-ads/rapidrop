
from pydantic import BaseModel, Field


class UpdateMerchantRequest(BaseModel):
    name: str | None = None
    business_name: str | None = None
    phone: str | None = None
    address: dict | None = None
    logo_url: str | None = None
    settings: dict | None = None


class UpdateSegmentRequest(BaseModel):
    segment: str


# --- Store Settings ---


class OperatingHours(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    open_time: str = Field(..., description="HH:MM format")
    close_time: str = Field(..., description="HH:MM format")
    is_open: bool = True


class DeliveryArea(BaseModel):
    type: str = Field(default="radius", description="radius or neighborhoods")
    radius_km: float | None = Field(default=None, ge=0)
    neighborhoods: list[str] | None = None
    base_address_lat: float | None = None
    base_address_lng: float | None = None


class DeliveryFee(BaseModel):
    type: str = Field(default="fixed", description="fixed, per_km, or free_above")
    fixed_fee_cents: int | None = Field(default=None, ge=0)
    per_km_cents: int | None = Field(default=None, ge=0)
    free_above_cents: int | None = Field(default=None, ge=0)


class StoreSettingsRequest(BaseModel):
    operating_hours: list[OperatingHours] | None = None
    delivery_area: DeliveryArea | None = None
    delivery_fee: DeliveryFee | None = None


class StoreSettingsResponse(BaseModel):
    operating_hours: list[dict] = []
    delivery_area: dict = {}
    delivery_fee: dict = {}


class LogoUploadResponse(BaseModel):
    logo_url: str
