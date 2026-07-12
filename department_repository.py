"""Department repository."""
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.department import Department
from repositories.base_repository import BaseRepository


class DepartmentRepository(BaseRepository[Department]):

    def __init__(self, db: AsyncSession):
        super().__init__(Department, db)

    async def get_by_code(self, code: str) -> Department | None:
        result = await self.db.execute(
            select(Department).where(and_(Department.code == code, Department.is_deleted == False))  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Department | None:
        result = await self.db.execute(
            select(Department).where(and_(Department.name == name, Department.is_deleted == False))  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def search(
        self, search: str = "", status: str = "", limit: int = 20, offset: int = 0
    ) -> tuple[list[Department], int]:
        filters = [Department.is_deleted == False]  # noqa: E712
        if search:
            filters.append(
                or_(
                    Department.name.ilike(f"%{search}%"),
                    Department.code.ilike(f"%{search}%"),
                    Department.description.ilike(f"%{search}%"),
                )
            )
        if status:
            filters.append(Department.status == status)

        total = (await self.db.execute(
            select(func.count()).select_from(Department).where(and_(*filters))
        )).scalar() or 0

        result = await self.db.execute(
            select(Department).where(and_(*filters))
            .order_by(Department.name.asc())
            .limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total
