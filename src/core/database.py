"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import get_settings

# Lazy database configuration
_engine = None
_SessionLocal = None


def get_engine():
    """Get database engine with lazy loading."""
    global _engine
    if _engine is None:
        settings = get_settings()
        try:
            _engine = create_engine(
                settings.database_url,
                echo=settings.debug,
            )
            # Test the connection
            with _engine.connect() as conn:
                from sqlalchemy import text

                conn.execute(text("SELECT 1"))
        except Exception as e:
            from src.core.logging_config import get_logger

            logger = get_logger(__name__)
            logger.critical(
                "Database connection failed - system cannot start",
                database_url=settings.database_url,
                error=str(e),
                exc_info=True,
            )
            raise
    return _engine


def get_session_local():
    """Get session factory with lazy loading."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal


# For backward compatibility
engine = get_engine()
SessionLocal = get_session_local()

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
