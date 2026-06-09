from fastapi import APIRouter
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.get("")
async def health_check():
    logger.info("health_check_called")
    return {"status": "ok", "version": "0.1.0"}
