from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from src.core.config import settings
from src.core.database import engine
from src.core.logging import setup_logging
from src.core.sentry import setup_sentry
from src.api.health import router as health_router


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

    Instrumentator().instrument(app).expose(app)

    return app


app = create_app()
