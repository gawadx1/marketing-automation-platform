from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.database import init_db, close_db, check_db_connection
from app.core.cache import close_redis
from app.core.middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    ExceptionHandlerMiddleware,
)
from app.core.exceptions import AppException
from app.api.routes import auth, campaigns, contacts, dashboard, newsletter, automation, health
from app.scheduler.scheduler import start_scheduler, stop_scheduler
from loguru import logger

settings = get_settings()
setup_logging()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri=settings.REDIS_URL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} ({settings.APP_ENV})")

    db_ok = await check_db_connection()
    if not db_ok:
        logger.warning("Starting without database - some features may be unavailable")

    await init_db()

    start_scheduler()

    yield

    logger.info("Shutting down...")
    stop_scheduler()
    await close_db()
    await close_redis()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade Marketing Automation & Reporting Platform",
    docs_url="/docs" if not settings.IS_PRODUCTION else None,
    redoc_url="/redoc" if not settings.IS_PRODUCTION else None,
    openapi_url="/openapi.json" if not settings.IS_PRODUCTION else None,
    lifespan=lifespan,
    contact={
        "name": "Marketing Platform Team",
        "url": "https://github.com/marketing-platform",
    },
    license_info={
        "name": "MIT",
    },
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=["X-Request-ID", "X-Response-Time-Ms"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ExceptionHandlerMiddleware)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
        headers=exc.headers,
    )


api_prefix = settings.API_PREFIX

app.include_router(auth.router, prefix=api_prefix)
app.include_router(campaigns.router, prefix=api_prefix)
app.include_router(contacts.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(newsletter.router, prefix=api_prefix)
app.include_router(automation.router, prefix=api_prefix)
app.include_router(health.router, prefix=api_prefix)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "docs": "/docs",
        "health": f"{api_prefix}/health",
    }
