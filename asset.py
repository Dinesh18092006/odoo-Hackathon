"""Asset model — core entity of the system."""
from typing import TYPE_CHECKING
from datetime import date
from sqlalchemy import String, Text, Float, Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .asset_category import AssetCategory
    from .department import Department
    from .user import User
    from .asset_image import AssetImage
    from .asset_document import AssetDocument
    from .allocation import Allocation
    from .transfer import Transfer
    from .booking import Booking
    from .maintenance import MaintenanceRequest
    from .audit import AuditItem


class Asset(BaseModel):
    """
    Physical asset entity.
    Lifecycle: available → allocated | reserved | under_maintenance → lost | retired → disposed
    """

    __tablename__ = "assets"
    __table_args__ = (
        Index("ix_assets_category_id", "category_id"),
        Index("ix_assets_department_id", "department_id"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    asset_tag: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vendor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    warranty_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    qr_code_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Status: available | allocated | reserved | under_maintenance | lost | retired | disposed
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="available", index=True)

    # Foreign keys
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("asset_categories.id"), nullable=False
    )
    department_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("departments.id"), nullable=True
    )

    # Relationships
    category: Mapped["AssetCategory"] = relationship("AssetCategory", back_populates="assets")
    department: Mapped["Department | None"] = relationship("Department", back_populates="assets")
    images: Mapped[list["AssetImage"]] = relationship(
        "AssetImage", back_populates="asset", cascade="all, delete-orphan"
    )
    documents: Mapped[list["AssetDocument"]] = relationship(
        "AssetDocument", back_populates="asset", cascade="all, delete-orphan"
    )
    allocations: Mapped[list["Allocation"]] = relationship(
        "Allocation", back_populates="asset", order_by="Allocation.created_at.desc()"
    )
    transfers: Mapped[list["Transfer"]] = relationship(
        "Transfer", back_populates="asset", order_by="Transfer.created_at.desc()"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="asset", order_by="Booking.created_at.desc()"
    )
    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest", back_populates="asset", order_by="MaintenanceRequest.created_at.desc()"
    )
    audit_items: Mapped[list["AuditItem"]] = relationship("AuditItem", back_populates="asset")

    def __repr__(self) -> str:
        return f"<Asset {self.asset_tag}: {self.name} [{self.status}]>"
