from datetime import datetime

from pydantic import BaseModel, Field

# --- Product ---


class ProductCreate(BaseModel):
    category_id: str | None = None
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price_cents: int = Field(..., ge=0)
    barcode: str | None = Field(default=None, max_length=50)
    unit_type: str = Field(default="unit")
    is_available: bool = True
    stock_quantity: int | None = None
    stock_alert_at: int | None = None
    segment_specific: dict = Field(default_factory=dict)


class ProductUpdate(BaseModel):
    category_id: str | None = None
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price_cents: int | None = Field(default=None, ge=0)
    image_url: str | None = None
    barcode: str | None = Field(default=None, max_length=50)
    unit_type: str | None = None
    is_available: bool | None = None
    has_variations: bool | None = None
    stock_quantity: int | None = None
    stock_alert_at: int | None = None
    segment_specific: dict | None = None


class VariationItem(BaseModel):
    id: str
    name: str
    price_cents_adjustment: int
    is_default: bool


class ProductResponse(BaseModel):
    id: str
    category_id: str | None
    category_name: str | None = None
    name: str
    description: str | None
    price_cents: int
    price_formatted: str = ""
    image_url: str | None
    barcode: str | None
    unit_type: str
    is_available: bool
    has_variations: bool
    stock_quantity: int | None
    stock_alert_at: int | None
    variations: list[VariationItem] = []
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int


class AvailabilityToggle(BaseModel):
    """Request body for toggling product availability."""

    is_available: bool


class PhotoUploadResponse(BaseModel):
    """Response after uploading a product photo."""

    image_url: str


# --- Variations ---


class VariationCreate(BaseModel):
    name: str = Field(..., max_length=255)
    price_cents_adjustment: int = Field(default=0)
    is_default: bool = False


class VariationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    price_cents_adjustment: int | None = None
    is_default: bool | None = None


class VariationResponse(BaseModel):
    id: str
    product_id: str
    name: str
    price_cents_adjustment: int
    is_default: bool
    created_at: datetime
