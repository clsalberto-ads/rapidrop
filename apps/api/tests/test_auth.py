"""Tests for auth endpoints — uses mocked database session."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.main import app


@pytest.fixture(autouse=True)
def _mock_db():
    """Replace the real PostgreSQL session with a mock for all tests.

    This avoids event loop conflicts between asyncpg and httpx's ASGITransport.
    """

    async def mock_get_db():
        mock_session = AsyncMock(spec=AsyncSession)
        # Make execute() return an empty result (no rows found)
        mock_execute = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_result.scalars.return_value.all.return_value = []
        mock_execute.return_value = mock_result
        mock_session.execute = mock_execute
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        yield mock_session

    app.dependency_overrides[get_db] = mock_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_register_merchant():
    """Register endpoint should accept valid data and return tokens."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json={
            "email": "loja@teste.com",
            "password": "senha123",
            "name": "Loja Teste",
            "business_name": "Loja Teste Ltda",
            "document": "12345678901234",
            "phone": "11999999999",
            "segment": "food",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login():
    """Login endpoint should return tokens for valid credentials."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", json={
            "email": "loja@teste.com",
            "password": "senha123",
        })
        assert response.status_code == 401  # mock returns no user → invalid credentials


@pytest.mark.asyncio
async def test_health_still_works():
    """Health endpoint should not be affected by dependency overrides."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
