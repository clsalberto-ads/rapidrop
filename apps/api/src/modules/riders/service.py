import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.rider import Rider

logger = structlog.get_logger()


def _rider_query():
    """Base rider query."""
    return select(Rider)


async def list_riders(
    db: AsyncSession,
    merchant_id: str,
    only_active: bool = False,
    only_online: bool = False,
    search: str | None = None,
) -> tuple[list[Rider], int]:
    """List riders for a merchant with optional filters."""
    query = _rider_query().where(Rider.merchant_id == merchant_id)

    if only_active:
        query = query.where(Rider.is_active.is_(True))

    if only_online:
        query = query.where(Rider.is_online.is_(True))

    if search:
        query = query.where(
            Rider.name.ilike(f"%{search}%") | Rider.phone.ilike(f"%{search}%")
        )

    query = query.order_by(Rider.name)

    result = await db.execute(query)
    riders = list(result.scalars().all())
    total = len(riders)
    return riders, total


async def get_rider(db: AsyncSession, rider_id: str, merchant_id: str) -> Rider | None:
    """Get a single rider by id, scoped to merchant."""
    result = await db.execute(
        _rider_query().where(
            Rider.id == rider_id,
            Rider.merchant_id == merchant_id,
        )
    )
    return result.scalar_one_or_none()


async def create_rider(db: AsyncSession, merchant_id: str, data: dict) -> Rider:
    """Create a new rider."""
    rider = Rider(merchant_id=merchant_id, **data)
    db.add(rider)
    await db.commit()
    await db.refresh(rider)
    logger.info("rider_created", merchant_id=merchant_id, rider_id=str(rider.id))
    return rider


async def update_rider(
    db: AsyncSession, rider_id: str, merchant_id: str, data: dict
) -> Rider | None:
    """Update a rider."""
    rider = await get_rider(db, rider_id, merchant_id)
    if not rider:
        return None

    for field, value in data.items():
        if value is not None:
            setattr(rider, field, value)

    await db.commit()
    await db.refresh(rider)
    logger.info("rider_updated", merchant_id=merchant_id, rider_id=str(rider.id))
    return rider


async def delete_rider(db: AsyncSession, rider_id: str, merchant_id: str) -> bool:
    """Soft-delete a rider (set is_active=False)."""
    rider = await get_rider(db, rider_id, merchant_id)
    if not rider:
        return False

    rider.is_active = False
    await db.commit()
    logger.info("rider_deactivated", merchant_id=merchant_id, rider_id=str(rider_id))
    return True
