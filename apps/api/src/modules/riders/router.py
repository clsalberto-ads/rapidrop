import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.deps import extract_merchant_id, get_current_merchant
from src.modules.riders.schemas import (
    RiderCreate,
    RiderListResponse,
    RiderResponse,
    RiderUpdate,
)
from src.modules.riders.service import (
    create_rider,
    delete_rider,
    get_rider,
    list_riders,
    update_rider,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/riders", tags=["riders"])


def _rider_to_response(rider) -> RiderResponse:
    return RiderResponse(
        id=str(rider.id),
        name=rider.name,
        phone=rider.phone,
        vehicle_type=rider.vehicle_type.value if hasattr(rider.vehicle_type, "value") else str(rider.vehicle_type),
        document=rider.document,
        pix_key=rider.pix_key,
        is_online=rider.is_online,
        is_active=rider.is_active,
        current_location=rider.current_location or {},
        created_at=rider.created_at,
        updated_at=rider.updated_at,
    )


@router.get("", response_model=RiderListResponse)
async def list_riders_endpoint(
    only_active: bool = Query(default=False),
    only_online: bool = Query(default=False),
    search: str | None = Query(default=None),
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """List riders for the authenticated merchant."""
    merchant_id = extract_merchant_id(current_merchant)
    riders, total = await list_riders(
        db, merchant_id, only_active=only_active, only_online=only_online, search=search
    )
    return RiderListResponse(
        riders=[_rider_to_response(r) for r in riders],
        total=total,
    )


@router.get("/{rider_id}", response_model=RiderResponse)
async def get_rider_endpoint(
    rider_id: str,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Get a single rider by ID."""
    merchant_id = extract_merchant_id(current_merchant)
    rider = await get_rider(db, rider_id, merchant_id)

    if not rider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

    return _rider_to_response(rider)


@router.post("", response_model=RiderResponse, status_code=status.HTTP_201_CREATED)
async def create_rider_endpoint(
    body: RiderCreate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Create a new rider."""
    merchant_id = extract_merchant_id(current_merchant)
    rider = await create_rider(db, merchant_id, body.model_dump())
    return _rider_to_response(rider)


@router.put("/{rider_id}", response_model=RiderResponse)
async def update_rider_endpoint(
    rider_id: str,
    body: RiderUpdate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Update a rider."""
    merchant_id = extract_merchant_id(current_merchant)
    rider = await update_rider(db, rider_id, merchant_id, body.model_dump(exclude_none=True))

    if not rider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")

    return _rider_to_response(rider)


@router.delete("/{rider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rider_endpoint(
    rider_id: str,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a rider (set is_active=False)."""
    merchant_id = extract_merchant_id(current_merchant)
    deleted = await delete_rider(db, rider_id, merchant_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found")
