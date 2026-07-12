"""Asset Category model."""
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .asset import Asset


class AssetCategory(BaseModel):
    """Asset type classification (e.g., Laptop, Projector, Vehicle)."""

    __tablename__ = "asset_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    depreciation_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    useful_life_years: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    # Relationships
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="category")

    def __repr__(self) -> str:
        return f"<AssetCategory {self.code}: {self.name}>"
