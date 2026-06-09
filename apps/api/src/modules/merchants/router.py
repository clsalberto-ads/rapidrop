import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.deps import get_current_merchant
from src.modules.auth.schemas import MerchantMeResponse
from src.modules.merchants.schemas import UpdateMerchantRequest, UpdateSegmentRequest
from src.modules.merchants.service import get_merchant_by_id, update_merchant, update_segment

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/merchants", tags=["merchants"])


@router.get("/me", response_model=MerchantMeResponse)
async def get_my_merchant(
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    merchant_id = current_merchant.get("sub")
    merchant = await get_merchant_by_id(db, merchant_id)

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
