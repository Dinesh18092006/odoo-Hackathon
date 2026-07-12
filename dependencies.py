"""
FastAPI dependency injection for authentication.
Extracts and validates the JWT token from the Authorization header.
"""
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth.jwt_handler import decode_access_token
from utils.exceptions import UnauthorizedException, NotFoundException

security = HTTPBearer()


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Extract and decode the JWT token.
    Returns the full payload dict with sub, email, role, department_id.
    """
    return decode_access_token(credentials.credentials)


async def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch the current user from the database using the JWT sub claim.
    Raises 401 if user not found or inactive.
    """
    from repositories.user_repository import UserRepository

    user_id = payload.get("sub")
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    if not user or user.is_deleted:
        raise UnauthorizedException("User account not found")

    if user.status != "active":
        raise UnauthorizedException("User account is not active")

    return user
