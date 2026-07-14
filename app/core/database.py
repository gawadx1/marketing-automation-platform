import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.core.config import get_settings
from loguru import logger

settings = get_settings()

_engine: AsyncEngine = None
_session_factory: async_sessionmaker = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            },
        )
    return _engine


def get_session_factory() -> async_sessionmaker:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database session rollback due to: {exc}")
            raise
        finally:
            await session.close()


async def check_db_connection(max_retries: int = 3, retry_delay: int = 2) -> bool:
    for attempt in range(1, max_retries + 1):
        try:
            engine = get_engine()
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
        except Exception as exc:
            logger.warning(f"Database connection attempt {attempt}/{max_retries} failed: {exc}")
            if attempt < max_retries:
                await asyncio.sleep(retry_delay * attempt)
    logger.error("All database connection attempts failed")
    return False


async def init_db():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")


async def close_db():
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("Database engine disposed")


def get_db_sync_url() -> str:
    return settings.DATABASE_URL_SYNC
