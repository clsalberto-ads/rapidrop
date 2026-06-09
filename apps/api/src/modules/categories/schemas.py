from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=255)
    sort_order: int = Field(default=0, ge=0)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    segment_fields: dict | None = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    sort_order: int
    is_active: bool
    product_count: int = 0
    created_at: datetime


class CategoryListResponse(BaseModel):
    categories: list[CategoryResponse]
    total: int
