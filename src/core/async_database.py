"""
Async database configuration and session management.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Create async database engine
async_engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for async models
AsyncBase = declarative_base()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
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
    async with async_engine.begin() as conn:
        await conn.run_sync(AsyncBase.metadata.create_all)


async def drop_async_tables():
    """Drop all database tables asynchronously."""
    async with async_engine.begin() as conn:
        await conn.run_sync(AsyncBase.metadata.drop_all)
