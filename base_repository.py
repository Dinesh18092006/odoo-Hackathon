"""Base repository with common CRUD operations."""
from typing import TypeVar, Generic, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, and_
from models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing CRUD operations for any SQLAlchemy model.
    All queries automatically filter out soft-deleted records.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, record_id: str) -> ModelType | None:
        """Fetch a single record by its UUID primary key."""
        result = await self.db.execute(
            select(self.model).where(
                and_(self.model.id == record_id, self.model.is_deleted == False)  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        filters: list | None = None,
        order_by=None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ModelType], int]:
        """
        Fetch paginated records with optional filters.
        Returns (records, total_count).
        """
        base_filter = [self.model.is_deleted == False]  # noqa: E712
        if filters:
            base_filter.extend(filters)

        # Count query
        count_stmt = select(func.count()).select_from(self.model).where(and_(*base_filter))
        total = (await self.db.execute(count_stmt)).scalar() or 0

        # Data query
        stmt = select(self.model).where(and_(*base_filter))
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(self.model.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        records = list(result.scalars().all())

        return records, total

    async def create(self, **kwargs) -> ModelType:
        """Create a new record and return it."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update(self, record_id: str, **kwargs) -> ModelType | None:
        """Update fields on a record. Returns the updated record or None."""
        from datetime import datetime, timezone
        kwargs["updated_at"] = datetime.now(timezone.utc)

        await self.db.execute(
            update(self.model)
            .where(and_(self.model.id == record_id, self.model.is_deleted == False))  # noqa: E712
            .values(**kwargs)
        )
        await self.db.flush()
        return await self.get_by_id(record_id)

    async def soft_delete(self, record_id: str) -> bool:
        """Soft-delete a record by setting is_deleted=True."""
        from datetime import datetime, timezone
        result = await self.db.execute(
            update(self.model)
            .where(and_(self.model.id == record_id, self.model.is_deleted == False))  # noqa: E712
            .values(is_deleted=True, updated_at=datetime.now(timezone.utc))
        )
        await self.db.flush()
        return result.rowcount > 0

    async def count(self, filters: list | None = None) -> int:
        """Count records matching given filters."""
        base_filter = [self.model.is_deleted == False]  # noqa: E712
        if filters:
            base_filter.extend(filters)
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(and_(*base_filter))
        )
        return result.scalar() or 0
