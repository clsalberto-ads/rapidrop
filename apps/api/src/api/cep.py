from fastapi import APIRouter, HTTPException

from src.integrations.viacep import lookup_cep

router = APIRouter(prefix="/api/v1/cep", tags=["cep"])


@router.get("/{cep}")
async def search_cep(cep: str):
    result = await lookup_cep(cep)
    if not result:
        raise HTTPException(status_code=404, detail="CEP not found")
    return result
