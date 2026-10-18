"""
Clisonix Database Session Management
Async SQLAlchemy configuration with connection pooling
"""
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from .configuration import database_url, engine_options

try:
    from ..settings import settings
except ImportError:
    from settings import settings

logger = logging.getLogger(__name__)

# Create async engine with connection pooling
_database_url = database_url(settings.database_url, asynchronous=True)
engine = create_async_engine(
    _database_url,
    echo=settings.database_echo,
    **engine_options(_database_url, asynchronous=True),
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    try:
        from ..auth.models import Base
    except ImportError:
        from auth.models import Base

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("âœ“ Database tables created successfully")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("âœ“ Database connections closed")


# Health check for database
async def check_db_health() -> bool:
    """Check database connectivity"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


