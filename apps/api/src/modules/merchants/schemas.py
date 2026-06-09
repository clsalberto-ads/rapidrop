
from pydantic import BaseModel


class UpdateMerchantRequest(BaseModel):
    name: str | None = None
    business_name: str | None = None
    phone: str | None = None
    address: dict | None = None
    logo_url: str | None = None
    settings: dict | None = None


class UpdateSegmentRequest(BaseModel):
    segment: str
