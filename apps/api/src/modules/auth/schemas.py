from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    business_name: str
    document: str
    phone: str
    segment: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class MerchantMeResponse(BaseModel):
    id: str
    email: str
    name: str
    business_name: str
    document: str
    phone: str
    segment: str
    is_active: bool
    created_at: str
