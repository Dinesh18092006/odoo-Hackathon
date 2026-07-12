"""Booking model for resource scheduling."""
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .asset import Asset
    from .user import User


class Booking(BaseModel):
    """
    Resource booking record with time-slot conflict detection.
    Status flow: pending → confirmed → completed | cancelled
    """

    __tablename__ = "bookings"
    __table_args__ = (
        Index("ix_bookings_asset_id", "asset_id"),
        Index("ix_bookings_booked_by", "booked_by"),
        Index("ix_bookings_status", "status"),
        Index("ix_bookings_start_time", "start_time"),
    )

    asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assets.id"), nullable=False
    )
    booked_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status: pending | confirmed | completed | cancelled
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="bookings")
    booked_by_user: Mapped["User"] = relationship(
        "User", back_populates="bookings", foreign_keys=[booked_by]
    )
