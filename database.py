"""
Async SQLAlchemy database engine and session factory.
Uses SQLite + aiosqlite for development (no installation required).
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import settings


# Create the async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class shared by all models."""
    pass


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides a database session.
    Session is automatically closed after the request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_all_tables() -> None:
    """Create all database tables on application startup."""
    async with engine.begin() as conn:
        # Import all models so SQLAlchemy registers them
        from models import (  # noqa: F401
            user, department, asset_category, asset,
            asset_image, asset_document, allocation, transfer,
            booking, maintenance, audit, notification, activity_log,
        )
        await conn.run_sync(Base.metadata.create_all)
