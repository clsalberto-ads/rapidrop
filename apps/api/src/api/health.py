import structlog
from fastapi import APIRouter

logger = structlog.get_logger()
router = APIRouter()


@router.get("")
async def health_check():
    logger.info("health_check_called")
    return {"status": "ok", "version": "0.1.0"}
