"""Constants and enumerations used across the entire application."""
from enum import Enum


class UserRole(str, Enum):
    """User role values."""
    ADMIN = "admin"
    ASSET_MANAGER = "asset_manager"
    DEPARTMENT_HEAD = "department_head"
    EMPLOYEE = "employee"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class AssetStatus(str, Enum):
    """Asset lifecycle states."""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    UNDER_MAINTENANCE = "under_maintenance"
    LOST = "lost"
    RETIRED = "retired"
    DISPOSED = "disposed"


# Valid state transitions for assets
ASSET_VALID_TRANSITIONS: dict[str, list[str]] = {
    AssetStatus.AVAILABLE: [
        AssetStatus.ALLOCATED,
        AssetStatus.RESERVED,
        AssetStatus.UNDER_MAINTENANCE,
        AssetStatus.LOST,
        AssetStatus.RETIRED,
    ],
    AssetStatus.ALLOCATED: [
        AssetStatus.AVAILABLE,
        AssetStatus.UNDER_MAINTENANCE,
        AssetStatus.LOST,
    ],
    AssetStatus.RESERVED: [
        AssetStatus.AVAILABLE,
        AssetStatus.LOST,
    ],
    AssetStatus.UNDER_MAINTENANCE: [
        AssetStatus.AVAILABLE,
        AssetStatus.LOST,
    ],
    AssetStatus.LOST: [
        AssetStatus.RETIRED,
    ],
    AssetStatus.RETIRED: [
        AssetStatus.DISPOSED,
    ],
    AssetStatus.DISPOSED: [],
}


class AllocationStatus(str, Enum):
    """Asset allocation workflow states."""
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    RETURNED = "returned"
    REJECTED = "rejected"


class TransferStatus(str, Enum):
    """Asset transfer workflow states."""
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    REJECTED = "rejected"


class BookingStatus(str, Enum):
    """Resource booking states."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenanceStatus(str, Enum):
    """Maintenance request workflow states."""
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class MaintenancePriority(str, Enum):
    """Maintenance priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditStatus(str, Enum):
    """Audit cycle states."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CLOSED = "closed"


class AuditItemStatus(str, Enum):
    """Individual asset verification states."""
    PENDING = "pending"
    VERIFIED = "verified"
    MISSING = "missing"
    DAMAGED = "damaged"


class NotificationType(str, Enum):
    """All notification event types."""
    ASSET_ASSIGNED = "ASSET_ASSIGNED"
    ALLOCATION_REJECTED = "ALLOCATION_REJECTED"
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    BOOKING_REMINDER = "BOOKING_REMINDER"
    MAINTENANCE_APPROVED = "MAINTENANCE_APPROVED"
    MAINTENANCE_REJECTED = "MAINTENANCE_REJECTED"
    MAINTENANCE_RESOLVED = "MAINTENANCE_RESOLVED"
    TRANSFER_APPROVED = "TRANSFER_APPROVED"
    TRANSFER_REJECTED = "TRANSFER_REJECTED"
    AUDIT_CREATED = "AUDIT_CREATED"
    AUDIT_CLOSED = "AUDIT_CLOSED"
    OVERDUE_RETURN = "OVERDUE_RETURN"
    ROLE_CHANGED = "ROLE_CHANGED"


class DocumentType(str, Enum):
    """Asset document categories."""
    INVOICE = "invoice"
    WARRANTY = "warranty"
    MANUAL = "manual"
    INSURANCE = "insurance"
    INSPECTION = "inspection"
    OTHER = "other"


# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# File upload constraints
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_DOCUMENT_MIME_TYPES = {"application/pdf"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
