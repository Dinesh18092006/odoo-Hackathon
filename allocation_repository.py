"""Allocation repository."""
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.allocation import Allocation
from repositories.base_repository import BaseRepository


class AllocationRepository(BaseRepository[Allocation]):

    def __init__(self, db: AsyncSession):
        super().__init__(Allocation, db)

    async def get_active_allocation_for_asset(self, asset_id: str) -> Allocation | None:
        """Check if an asset has an active or approved allocation."""
        result = await self.db.execute(
            select(Allocation).where(
                and_(
                    Allocation.asset_id == asset_id,
                    Allocation.status.in_(["approved", "active"]),
                    Allocation.is_deleted == False,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_with_details(self, allocation_id: str) -> Allocation | None:
        result = await self.db.execute(
            select(Allocation)
            .options(
                selectinload(Allocation.asset),
                selectinload(Allocation.allocated_to_user),
                selectinload(Allocation.allocated_by_user),
            )
            .where(and_(Allocation.id == allocation_id, Allocation.is_deleted == False))  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        search: str = "",
        status: str = "",
        asset_id: str = "",
        user_id: str = "",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Allocation], int]:
        filters = [Allocation.is_deleted == False]  # noqa: E712
        if status:
            filters.append(Allocation.status == status)
        if asset_id:
            filters.append(Allocation.asset_id == asset_id)
        if user_id:
            filters.append(
                or_(Allocation.allocated_to == user_id, Allocation.allocated_by == user_id)
            )

        total = (await self.db.execute(
            select(func.count()).select_from(Allocation).where(and_(*filters))
        )).scalar() or 0

        result = await self.db.execute(
            select(Allocation)
            .options(
                selectinload(Allocation.asset),
                selectinload(Allocation.allocated_to_user),
                selectinload(Allocation.allocated_by_user),
            )
            .where(and_(*filters))
            .order_by(Allocation.created_at.desc())
            .limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def count_pending(self) -> int:
        return await self.count([Allocation.status == "pending"])

    async def count_overdue(self) -> int:
        """Count active allocations past their expected return date."""
        from datetime import date
        return await self.count([
            Allocation.status == "active",
            Allocation.expected_return_date < date.today(),
        ])
