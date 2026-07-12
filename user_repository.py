"""User repository."""
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(and_(User.email == email, User.is_deleted == False))  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def get_by_employee_id(self, employee_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(and_(User.employee_id == employee_id, User.is_deleted == False))  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def search(
        self, search: str = "", role: str = "", department_id: str = "",
        status: str = "", limit: int = 20, offset: int = 0
    ) -> tuple[list[User], int]:
        filters = [User.is_deleted == False]  # noqa: E712
        if search:
            filters.append(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.employee_id.ilike(f"%{search}%"),
                )
            )
        if role:
            filters.append(User.role == role)
        if department_id:
            filters.append(User.department_id == department_id)
        if status:
            filters.append(User.status == status)

        from sqlalchemy import func
        total = (await self.db.execute(
            select(func.count()).select_from(User).where(and_(*filters))
        )).scalar() or 0

        result = await self.db.execute(
            select(User).where(and_(*filters))
            .order_by(User.full_name.asc())
            .limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total
