"""Asset Transfer model."""
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .asset import Asset
    from .user import User


class Transfer(BaseModel):
    """
    Asset transfer record — moves asset from one user/dept to another.
    Status flow: pending → approved → completed | rejected
    """

    __tablename__ = "transfers"
    __table_args__ = (
        Index("ix_transfers_asset_id", "asset_id"),
        Index("ix_transfers_status", "status"),
    )

    asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assets.id"), nullable=False
    )
    from_user: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    to_user: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    requested_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status: pending | approved | completed | rejected
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="transfers")
    from_user_obj: Mapped["User"] = relationship(
        "User", back_populates="transfers_from", foreign_keys=[from_user]
    )
    to_user_obj: Mapped["User"] = relationship(
        "User", back_populates="transfers_to", foreign_keys=[to_user]
    )
    requested_by_user: Mapped["User"] = relationship(
        "User", foreign_keys=[requested_by]
    )
