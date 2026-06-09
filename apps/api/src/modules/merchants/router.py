import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.deps import get_current_merchant
from src.modules.auth.schemas import MerchantMeResponse
from src.modules.merchants.schemas import (
    LogoUploadResponse,
    StoreSettingsRequest,
    StoreSettingsResponse,
    UpdateMerchantRequest,
    UpdateSegmentRequest,
)
from src.modules.merchants.service import get_merchant_by_id, update_merchant, update_segment

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/merchants", tags=["merchants"])


def _merchant_to_response(merchant) -> MerchantMeResponse:
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


@router.get("/me", response_model=MerchantMeResponse)
async def get_my_merchant(
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    merchant_id = current_merchant.get("sub")
    merchant = await get_merchant_by_id(db, merchant_id)

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    return _merchant_to_response(merchant)


@router.put("/me", response_model=MerchantMeResponse)
async def update_my_merchant(
    body: UpdateMerchantRequest,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    merchant_id = current_merchant.get("sub")
    merchant = await update_merchant(db, merchant_id, body.model_dump(exclude_none=True))

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    return _merchant_to_response(merchant)


@router.put("/me/segment", response_model=MerchantMeResponse)
async def update_my_segment(
    body: UpdateSegmentRequest,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    merchant_id = current_merchant.get("sub")
    merchant = await update_segment(db, merchant_id, body.segment)

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    return _merchant_to_response(merchant)


# --- Store Settings ---


@router.get("/me/settings", response_model=StoreSettingsResponse)
async def get_store_settings(
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Get store configuration: operating hours, delivery area, delivery fee."""
    merchant_id = current_merchant.get("sub")
    merchant = await get_merchant_by_id(db, merchant_id)

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    settings = merchant.settings or {}
    return StoreSettingsResponse(
        operating_hours=settings.get("operating_hours", []),
        delivery_area=settings.get("delivery_area", {}),
        delivery_fee=settings.get("delivery_fee", {}),
    )


@router.put("/me/settings", response_model=StoreSettingsResponse)
async def update_store_settings(
    body: StoreSettingsRequest,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Update store configuration: operating hours, delivery area, delivery fee."""
    merchant_id = current_merchant.get("sub")
    merchant = await get_merchant_by_id(db, merchant_id)

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    settings = merchant.settings or {}

    if body.operating_hours is not None:
        settings["operating_hours"] = [h.model_dump() for h in body.operating_hours]

    if body.delivery_area is not None:
        settings["delivery_area"] = body.delivery_area.model_dump()

    if body.delivery_fee is not None:
        settings["delivery_fee"] = body.delivery_fee.model_dump()

    merchant.settings = settings
    await db.commit()
    await db.refresh(merchant)

    logger.info("store_settings_updated", merchant_id=merchant_id)

    return StoreSettingsResponse(
        operating_hours=settings.get("operating_hours", []),
        delivery_area=settings.get("delivery_area", {}),
        delivery_fee=settings.get("delivery_fee", {}),
    )


@router.post("/me/logo", response_model=LogoUploadResponse)
async def upload_logo(
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Upload store logo. Returns a placeholder URL — file upload via MinIO/S3 is post-MVP."""
    merchant_id = current_merchant.get("sub")
    merchant = await get_merchant_by_id(db, merchant_id)

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    logger.info("logo_upload_placeholder", merchant_id=merchant_id)

    return LogoUploadResponse(
        logo_url=merchant.logo_url or f"https://placehold.co/400x400?text={merchant.name[:2].upper()}"
    )
