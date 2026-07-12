"""Department model."""
from typing import TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .asset import Asset
    from .audit import AuditCycle


class Department(BaseModel):
    """Organizational department entity."""

    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="department", foreign_keys="User.department_id"
    )
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="department")
    audit_cycles: Mapped[list["AuditCycle"]] = relationship(
        "AuditCycle", back_populates="department"
    )

    def __repr__(self) -> str:
        return f"<Department {self.code}: {self.name}>"
