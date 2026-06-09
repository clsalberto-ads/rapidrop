import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.merchant import Merchant, MerchantSegment
from src.models.onboarding import MerchantOnboarding
from src.modules.auth.deps import extract_merchant_id, get_current_merchant
from src.modules.auth.schemas import (
    LoginRequest,
    MerchantMeResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from src.modules.auth.service import create_tokens, decode_token, hash_password, verify_password

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    logger.info("auth_register_attempt", email=body.email)

    existing = await db.execute(select(Merchant).where(Merchant.email == body.email))
    if existing.scalar_one_or_none():
        logger.warning("auth_register_email_exists", email=body.email)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    merchant = Merchant(
        email=body.email,
        password_hash=hash_password(body.password),
        name=body.name,
        business_name=body.business_name,
        document=body.document,
        phone=body.phone,
        segment=MerchantSegment(body.segment),
    )
    db.add(merchant)
    await db.flush()

    onboarding = MerchantOnboarding(merchant_id=merchant.id)
    db.add(onboarding)
    await db.commit()
    await db.refresh(merchant)

    logger.info("auth_register_success", merchant_id=str(merchant.id))
    tokens = create_tokens(str(merchant.id))
    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    logger.info("auth_login_attempt", email=body.email)

    result = await db.execute(select(Merchant).where(Merchant.email == body.email))
    merchant = result.scalar_one_or_none()

    if not merchant or not verify_password(body.password, merchant.password_hash):
        logger.warning("auth_login_invalid_credentials", email=body.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    logger.info("auth_login_success", merchant_id=str(merchant.id))
    tokens = create_tokens(str(merchant.id))
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    logger.info("auth_refresh_attempt")

    payload = decode_token(body.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        logger.warning("auth_refresh_invalid_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    merchant_id = extract_merchant_id(payload)
    logger.info("auth_refresh_success", merchant_id=merchant_id)
    tokens = create_tokens(merchant_id)
    return TokenResponse(**tokens)


@router.get("/me", response_model=MerchantMeResponse)
async def me(
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    merchant_id = extract_merchant_id(current_merchant)
    result = await db.execute(select(Merchant).where(Merchant.id == merchant_id))
    merchant = result.scalar_one_or_none()

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    return MerchantMeResponse(
        id=str(merchant.id),
        email=merchant.email,
        name=merchant.name,
        business_name=merchant.business_name,
        document=merchant.document,
        phone=merchant.phone,
        segment=merchant.segment.value,
        is_active=merchant.is_active,
        created_at=merchant.created_at.isoformat(),
    )
