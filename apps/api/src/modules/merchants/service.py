import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.merchant import Merchant, MerchantSegment

logger = structlog.get_logger()


async def get_merchant_by_id(db: AsyncSession, merchant_id: str) -> Merchant | None:
    result = await db.execute(select(Merchant).where(Merchant.id == merchant_id))
    return result.scalar_one_or_none()


async def update_merchant(db: AsyncSession, merchant_id: str, data: dict) -> Merchant | None:
    merchant = await get_merchant_by_id(db, merchant_id)
    if not merchant:
        return None

    for field, value in data.items():
        if value is not None:
            setattr(merchant, field, value)

    await db.commit()
    await db.refresh(merchant)
    logger.info("merchant_updated", merchant_id=merchant_id, fields=list(data.keys()))
    return merchant


async def update_segment(db: AsyncSession, merchant_id: str, segment: str) -> Merchant | None:
    merchant = await get_merchant_by_id(db, merchant_id)
    if not merchant:
        return None

    merchant.segment = MerchantSegment(segment)
    await db.commit()
    await db.refresh(merchant)
    logger.info("merchant_segment_updated", merchant_id=merchant_id, segment=segment)
    return merchant
