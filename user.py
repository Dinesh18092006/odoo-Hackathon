"""User model with role-based access control."""
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .department import Department
    from .notification import Notification
    from .activity_log import ActivityLog
    from .allocation import Allocation
    from .transfer import Transfer
    from .booking import Booking
    from .maintenance import MaintenanceRequest
    from .audit import AuditCycle


class User(BaseModel):
    """
    System user entity.
    Roles: admin | asset_manager | department_head | employee
    Note: registration always creates 'employee' role.
    Only admin can promote roles.
    """

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
        Index("ix_users_department_id", "department_id"),
    )

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="employee")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    department_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    department: Mapped["Department | None"] = relationship(
        "Department", back_populates="users", foreign_keys=[department_id]
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="user"
    )
    allocations_received: Mapped[list["Allocation"]] = relationship(
        "Allocation", back_populates="allocated_to_user", foreign_keys="Allocation.allocated_to"
    )
    allocations_given: Mapped[list["Allocation"]] = relationship(
        "Allocation", back_populates="allocated_by_user", foreign_keys="Allocation.allocated_by"
    )
    transfers_from: Mapped[list["Transfer"]] = relationship(
        "Transfer", back_populates="from_user_obj", foreign_keys="Transfer.from_user"
    )
    transfers_to: Mapped[list["Transfer"]] = relationship(
        "Transfer", back_populates="to_user_obj", foreign_keys="Transfer.to_user"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="booked_by_user", foreign_keys="Booking.booked_by"
    )
    maintenance_raised: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest", back_populates="raised_by_user", foreign_keys="MaintenanceRequest.raised_by"
    )
    maintenance_assigned: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest", back_populates="assigned_technician_user",
        foreign_keys="MaintenanceRequest.assigned_technician"
    )
    audit_cycles_audited: Mapped[list["AuditCycle"]] = relationship(
        "AuditCycle", back_populates="assigned_auditor_user", foreign_keys="AuditCycle.assigned_auditor"
    )

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"
