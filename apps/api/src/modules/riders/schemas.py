from datetime import datetime

from pydantic import BaseModel, Field


class RiderCreate(BaseModel):
    name: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=20)
    vehicle_type: str = Field(...)
    document: str = Field(..., max_length=20)
    pix_key: str | None = Field(default=None, max_length=255)


class RiderUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    vehicle_type: str | None = None
    document: str | None = Field(default=None, max_length=20)
    pix_key: str | None = Field(default=None, max_length=255)


class RiderResponse(BaseModel):
    id: str
    name: str
    phone: str
    vehicle_type: str
    document: str
    pix_key: str | None
    is_online: bool
    is_active: bool
    current_location: dict
    created_at: datetime
    updated_at: datetime


class RiderListResponse(BaseModel):
    riders: list[RiderResponse]
    total: int
