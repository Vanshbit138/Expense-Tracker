"""
Async database configuration and session management.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.core.config import get_settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Lazy async database configuration
_async_engine = None
_AsyncSessionLocal = None
_AsyncBase = None


def get_async_engine():
    """Get async database engine with lazy loading."""
    global _async_engine
    if _async_engine is None:
        settings = get_settings()
        _async_engine = create_async_engine(
            settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=settings.debug,
            future=True,
        )
    return _async_engine


def get_async_session_local():
    """Get async session factory with lazy loading."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            get_async_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _AsyncSessionLocal


def get_async_base():
    """Get async base class with lazy loading."""
    global _AsyncBase
    if _AsyncBase is None:
        _AsyncBase = declarative_base()
    return _AsyncBase


# For backward compatibility
async_engine = get_async_engine()
AsyncSessionLocal = get_async_session_local()
AsyncBase = get_async_base()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""
    async with get_async_session_local()() as session:
        try:
            yield session
        except Exception as e:
            logger.error("Database session error", error=str(e), exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_async_tables():
    """Create all database tables asynchronously."""
    async with get_async_engine().begin() as conn:
        await conn.run_sync(get_async_base().metadata.create_all)


async def drop_async_tables():
    """Drop all database tables asynchronously."""
    async with get_async_engine().begin() as conn:
        await conn.run_sync(get_async_base().metadata.drop_all)
