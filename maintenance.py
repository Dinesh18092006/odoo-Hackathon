"""Maintenance Request model."""
from typing import TYPE_CHECKING
from datetime import date
from sqlalchemy import String, ForeignKey, Text, Date, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .asset import Asset
    from .user import User


class MaintenanceRequest(BaseModel):
    """
    Maintenance workflow entity.
    Status flow: pending → approved → in_progress → resolved | rejected
    When approved: asset status changes to under_maintenance
    When resolved: asset status reverts to available
    """

    __tablename__ = "maintenance_requests"
    __table_args__ = (
        Index("ix_maintenance_asset_id", "asset_id"),
        Index("ix_maintenance_status", "status"),
    )

    asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assets.id"), nullable=False
    )
    raised_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    assigned_technician: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    resolved_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[float] = mapped_column(default=0.0, nullable=False)

    # Status: pending | approved | in_progress | resolved | rejected
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenance_requests")
    raised_by_user: Mapped["User"] = relationship(
        "User", back_populates="maintenance_raised", foreign_keys=[raised_by]
    )
    assigned_technician_user: Mapped["User | None"] = relationship(
        "User", back_populates="maintenance_assigned", foreign_keys=[assigned_technician]
    )
