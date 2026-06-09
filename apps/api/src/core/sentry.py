from src.core.config import settings


def setup_sentry() -> None:
    if not settings.SENTRY_DSN:
        return

    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment="production" if not settings.DEBUG else "development",
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )
