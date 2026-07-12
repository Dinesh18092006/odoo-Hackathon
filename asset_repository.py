"""Asset repository with full search, filter and history support."""
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.asset import Asset
from repositories.base_repository import BaseRepository


class AssetRepository(BaseRepository[Asset]):

    def __init__(self, db: AsyncSession):
        super().__init__(Asset, db)

    async def get_by_tag(self, asset_tag: str) -> Asset | None:
        result = await self.db.execute(
            select(Asset).where(and_(Asset.asset_tag == asset_tag, Asset.is_deleted == False))  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def get_by_serial(self, serial_number: str) -> Asset | None:
        result = await self.db.execute(
            select(Asset).where(and_(Asset.serial_number == serial_number, Asset.is_deleted == False))  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def get_next_sequence(self) -> int:
        """Get the next sequence number for asset tag generation."""
        result = await self.db.execute(select(func.count()).select_from(Asset))
        return (result.scalar() or 0) + 1

    async def get_with_details(self, asset_id: str) -> Asset | None:
        """Fetch asset with all relationships loaded."""
        result = await self.db.execute(
            select(Asset)
            .options(
                selectinload(Asset.category),
                selectinload(Asset.department),
                selectinload(Asset.images),
                selectinload(Asset.documents),
            )
            .where(and_(Asset.id == asset_id, Asset.is_deleted == False))  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        search: str = "",
        status: str = "",
        category_id: str = "",
        department_id: str = "",
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Asset], int]:
        filters = [Asset.is_deleted == False]  # noqa: E712
        if search:
            filters.append(
                or_(
                    Asset.name.ilike(f"%{search}%"),
                    Asset.asset_tag.ilike(f"%{search}%"),
                    Asset.serial_number.ilike(f"%{search}%"),
                    Asset.location.ilike(f"%{search}%"),
                    Asset.vendor.ilike(f"%{search}%"),
                )
            )
        if status:
            filters.append(Asset.status == status)
        if category_id:
            filters.append(Asset.category_id == category_id)
        if department_id:
            filters.append(Asset.department_id == department_id)

        total = (await self.db.execute(
            select(func.count()).select_from(Asset).where(and_(*filters))
        )).scalar() or 0

        # Sorting
        sort_col = getattr(Asset, sort_by, Asset.created_at)
        order = sort_col.desc() if sort_order == "desc" else sort_col.asc()

        result = await self.db.execute(
            select(Asset)
            .options(selectinload(Asset.category), selectinload(Asset.department))
            .where(and_(*filters))
            .order_by(order)
            .limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def count_by_status(self) -> dict[str, int]:
        """Count assets grouped by status (for dashboard KPIs)."""
        result = await self.db.execute(
            select(Asset.status, func.count(Asset.id))
            .where(Asset.is_deleted == False)  # noqa: E712
            .group_by(Asset.status)
        )
        return {row[0]: row[1] for row in result.all()}
