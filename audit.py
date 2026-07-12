"""Audit Cycle and Audit Item models."""
from typing import TYPE_CHECKING
from datetime import date
from sqlalchemy import String, ForeignKey, Text, Date, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .department import Department
    from .asset import Asset


class AuditCycle(BaseModel):
    """
    An audit cycle covers a department's assets for a period.
    Status flow: draft → active → completed → closed
    """

    __tablename__ = "audit_cycles"
    __table_args__ = (
        Index("ix_audit_cycles_status", "status"),
        Index("ix_audit_cycles_department_id", "department_id"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    department_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("departments.id"), nullable=True
    )
    assigned_auditor: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status: draft | active | completed | closed
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    # Relationships
    department: Mapped["Department | None"] = relationship(
        "Department", back_populates="audit_cycles"
    )
    assigned_auditor_user: Mapped["User | None"] = relationship(
        "User", back_populates="audit_cycles_audited", foreign_keys=[assigned_auditor]
    )
    items: Mapped[list["AuditItem"]] = relationship(
        "AuditItem", back_populates="audit_cycle", cascade="all, delete-orphan"
    )


class AuditItem(BaseModel):
    """Individual asset verification record within an audit cycle."""

    __tablename__ = "audit_items"
    __table_args__ = (
        Index("ix_audit_items_audit_cycle_id", "audit_cycle_id"),
        Index("ix_audit_items_asset_id", "asset_id"),
    )

    audit_cycle_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("audit_cycles.id", ondelete="CASCADE"), nullable=False
    )
    asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assets.id"), nullable=False
    )
    verified_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    condition_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status: pending | verified | missing | damaged
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

    # Relationships
    audit_cycle: Mapped["AuditCycle"] = relationship("AuditCycle", back_populates="items")
    asset: Mapped["Asset"] = relationship("Asset", back_populates="audit_items")
    verified_by_user: Mapped["User | None"] = relationship("User", foreign_keys=[verified_by])
