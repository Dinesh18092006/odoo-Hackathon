"""
Role-Based Access Control (RBAC) decorators/dependencies.
Use these as FastAPI dependencies on route handlers.
"""
from fastapi import Depends
from utils.constants import UserRole
from utils.exceptions import PermissionDeniedException
from auth.dependencies import get_current_user
from models.user import User


def require_roles(*allowed_roles: str):
    """
    Factory that returns a dependency requiring one of the specified roles.
    Usage:
        @router.get("/admin-only")
        async def admin_route(user: User = Depends(require_roles("admin"))):
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedException(
                f"This action requires one of these roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker


# Pre-built role dependencies for common use cases
require_admin = require_roles(UserRole.ADMIN)

require_admin_or_manager = require_roles(UserRole.ADMIN, UserRole.ASSET_MANAGER)

require_admin_manager_or_head = require_roles(
    UserRole.ADMIN, UserRole.ASSET_MANAGER, UserRole.DEPARTMENT_HEAD
)

require_any_role = require_roles(
    UserRole.ADMIN, UserRole.ASSET_MANAGER, UserRole.DEPARTMENT_HEAD, UserRole.EMPLOYEE
)


def can_approve_allocation(current_user: User) -> bool:
    """Check if user can approve allocations."""
    return current_user.role in {UserRole.ADMIN, UserRole.ASSET_MANAGER, UserRole.DEPARTMENT_HEAD}


def can_register_assets(current_user: User) -> bool:
    """Check if user can register new assets."""
    return current_user.role in {UserRole.ADMIN, UserRole.ASSET_MANAGER}


def can_manage_users(current_user: User) -> bool:
    """Check if user can manage other users."""
    return current_user.role == UserRole.ADMIN
