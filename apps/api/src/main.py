from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.cep import router as cep_router
from src.api.health import router as health_router
from src.core.database import engine
from src.core.logging import setup_logging
from src.core.sentry import setup_sentry
from src.modules.auth.router import router as auth_router
from src.modules.categories.router import router as categories_router
from src.modules.merchants.router import router as merchants_router
from src.modules.onboarding.router import router as onboarding_router
from src.modules.orders.router import router as orders_router
from src.modules.products.router import router as products_router
from src.modules.riders.router import router as riders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    setup_sentry()
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="RapiDrop API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(cep_router)
    app.include_router(auth_router)
    app.include_router(merchants_router)
    app.include_router(onboarding_router)
    app.include_router(categories_router)
    app.include_router(products_router)
    app.include_router(orders_router)
    app.include_router(riders_router)

    Instrumentator().instrument(app).expose(app)

    return app


app = create_app()
