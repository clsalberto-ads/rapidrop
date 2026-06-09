from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TenantRepository:
    """Base repository com filtro obrigatório de merchant_id."""

    def __init__(self, db: AsyncSession, merchant_id: str):
        self.db = db
        self.merchant_id = merchant_id

    def _apply_tenant_filter(self, query):
        """Aplica filtro de merchant_id na query."""
        return query.where(text(f"merchant_id = '{self.merchant_id}'"))


async def configure_rls_session(db: AsyncSession, merchant_id: str) -> None:
    """Configura variável de sessão PostgreSQL para RLS."""
    await db.execute(
        text(f"SET app.current_merchant_id = '{merchant_id}'")
    )
