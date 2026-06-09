import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.uuid7 import utcnow
from src.models.onboarding import MerchantOnboarding, OnboardingEvent, OnboardingStatus

logger = structlog.get_logger()

STEPS_TOTAL = 5


async def get_or_create_onboarding(db: AsyncSession, merchant_id: str) -> MerchantOnboarding:
    result = await db.execute(
        select(MerchantOnboarding).where(MerchantOnboarding.merchant_id == merchant_id)
    )
    onboarding = result.scalar_one_or_none()

    if not onboarding:
        onboarding = MerchantOnboarding(merchant_id=merchant_id, status=OnboardingStatus.active)
        db.add(onboarding)
        await db.commit()
        await db.refresh(onboarding)
        logger.info("onboarding_created", merchant_id=merchant_id)

    return onboarding


async def advance_step(db: AsyncSession, merchant_id: str, step: int) -> MerchantOnboarding:
    onboarding = await get_or_create_onboarding(db, merchant_id)

    if onboarding.status == OnboardingStatus.completed:
        logger.warning("onboarding_already_completed", merchant_id=merchant_id)
        return onboarding

    if onboarding.status == OnboardingStatus.blocked:
        logger.warning("onboarding_blocked", merchant_id=merchant_id)
        return onboarding

    if step != onboarding.current_step + 1:
        logger.warning(
            "onboarding_invalid_step",
            merchant_id=merchant_id,
            expected=onboarding.current_step + 1,
            received=step,
        )
        return onboarding

    event = OnboardingEvent(
        onboarding_id=onboarding.id,
        event_type=f"step_{step}",
        metadata={"step": step, "previous_step": onboarding.current_step},
    )
    db.add(event)

    onboarding.current_step = step

    if step >= STEPS_TOTAL:
        await complete_onboarding(db, merchant_id)
    else:
        await db.commit()
        await db.refresh(onboarding)

    logger.info("onboarding_step_advanced", merchant_id=merchant_id, step=step)
    return onboarding


async def complete_onboarding(db: AsyncSession, merchant_id: str) -> MerchantOnboarding:
    result = await db.execute(
        select(MerchantOnboarding).where(MerchantOnboarding.merchant_id == merchant_id)
    )
    onboarding = result.scalar_one_or_none()

    if not onboarding:
        onboarding = MerchantOnboarding(merchant_id=merchant_id)
        db.add(onboarding)

    onboarding.status = OnboardingStatus.completed
    onboarding.completed_at = utcnow()

    event = OnboardingEvent(
        onboarding_id=onboarding.id,
        event_type="completed",
        metadata={"current_step": onboarding.current_step},
    )
    db.add(event)
    await db.commit()
    await db.refresh(onboarding)

    logger.info("onboarding_completed", merchant_id=merchant_id)
    return onboarding


async def get_onboarding_status(db: AsyncSession, merchant_id: str) -> MerchantOnboarding:
    onboarding = await get_or_create_onboarding(db, merchant_id)
    return onboarding
