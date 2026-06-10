from datetime import datetime

from pydantic import BaseModel, Field


class OrderItemSchema(BaseModel):
    product_id: str
    product_name: str
    product_variation: str | None = None
    quantity: int = Field(..., ge=1)
    unit_price_cents: int = Field(..., ge=0)
    total_cents: int = Field(..., ge=0)
    special_notes: str | None = None


class OrderCreate(BaseModel):
    customer_id: str
    channel: str = "app"
    items: list[OrderItemSchema]
    subtotal_cents: int = Field(..., ge=0)
    delivery_fee_cents: int = 0
    discount_cents: int = 0
    total_cents: int = Field(..., ge=0)
    payment_method: str = "pix"
    customer_address: dict = Field(default_factory=dict)
    customer_notes: str | None = None
    segment_data: dict = Field(default_factory=dict)


class OrderUpdate(BaseModel):
    status: str | None = None
    payment_status: str | None = None
    rider_id: str | None = None
    customer_notes: str | None = None


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_variation: str | None
    quantity: int
    unit_price_cents: int
    total_cents: int
    special_notes: str | None


class OrderResponse(BaseModel):
    id: str
    sequential_id: int
    customer_id: str
    rider_id: str | None
    channel: str
    status: str
    items: list[OrderItemResponse]
    subtotal_cents: int
    delivery_fee_cents: int
    discount_cents: int
    total_cents: int
    payment_method: str
    payment_status: str
    customer_address: dict
    customer_notes: str | None
    confirmed_at: datetime | None
    preparing_at: datetime | None
    ready_at: datetime | None
    out_for_delivery_at: datetime | None
    delivered_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
