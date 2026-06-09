from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.service import decode_token

security = HTTPBearer()


def extract_merchant_id(payload: dict) -> str:
    """Safely extract merchant_id (sub) from a validated JWT payload.

    Guaranteed to exist after get_current_merchant validates the token.
    Raises 401 if missing (should never happen with valid tokens).
    """
    merchant_id = payload.get("sub")
    if not isinstance(merchant_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return merchant_id


async def get_current_merchant(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload


async def get_merchant_id(
    current_merchant: dict = Depends(get_current_merchant),
) -> str:
    return extract_merchant_id(current_merchant)
