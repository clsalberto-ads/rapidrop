import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.onboarding import OnboardingStatus
from src.modules.auth.deps import extract_merchant_id, get_current_merchant
from src.modules.onboarding.schemas import OnboardingStatusResponse
from src.modules.onboarding.service import advance_step, get_or_create_onboarding

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_status(
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    merchant_id = extract_merchant_id(current_merchant)
    onboarding = await get_or_create_onboarding(db, merchant_id)

    return OnboardingStatusResponse(
        current_step=onboarding.current_step,
        status=onboarding.status.value,
        completed_at=onboarding.completed_at.isoformat() if onboarding.completed_at else None,
    )


@router.post("/step/{step}", response_model=OnboardingStatusResponse)
async def post_step(
    step: int,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    merchant_id = extract_merchant_id(current_merchant)
    onboarding = await advance_step(db, merchant_id, step)

    if onboarding.status == OnboardingStatus.blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Onboarding is blocked")

    return OnboardingStatusResponse(
        current_step=onboarding.current_step,
        status=onboarding.status.value,
        completed_at=onboarding.completed_at.isoformat() if onboarding.completed_at else None,
    )
