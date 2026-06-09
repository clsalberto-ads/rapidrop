
import httpx
from pydantic import BaseModel


class ViaCEPReturn(BaseModel):
    zipcode: str
    street: str
    neighborhood: str
    city: str
    state: str


async def lookup_cep(cep: str) -> ViaCEPReturn | None:
    clean_cep = cep.replace("-", "").replace(".", "")
    if len(clean_cep) != 8:
        return None
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://viacep.com.br/ws/{clean_cep}/json/")
        if response.status_code != 200 or response.json().get("erro"):
            return None
        data = response.json()
        return ViaCEPReturn(
            zipcode=data["cep"],
            street=data["logradouro"],
            neighborhood=data["bairro"],
            city=data["localidade"],
            state=data["uf"],
        )
