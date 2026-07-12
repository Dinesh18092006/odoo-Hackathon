"""Activity Log model — immutable audit trail."""
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .user import User


class ActivityLog(BaseModel):
    """
    Immutable activity log entry.
    Every significant action in the system creates a log entry.
    Logs are never deleted.
    """

    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_user_id", "user_id"),
        Index("ix_activity_logs_module", "module"),
        Index("ix_activity_logs_created_at", "created_at"),
    )

    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    user_name: Mapped[str] = mapped_column(String(255), nullable=False, default="System")
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    record_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    record_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="activity_logs")
