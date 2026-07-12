"""Pagination utility — standard response structure for all list endpoints."""
from dataclasses import dataclass
from math import ceil
from utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


@dataclass
class PaginationParams:
    """Pagination parameters extracted from query string."""
    page: int = 1
    per_page: int = DEFAULT_PAGE_SIZE

    def __post_init__(self):
        self.page = max(1, self.page)
        self.per_page = max(1, min(self.per_page, MAX_PAGE_SIZE))

    @property
    def offset(self) -> int:
        """SQL OFFSET value."""
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        """SQL LIMIT value."""
        return self.per_page


@dataclass
class PaginationMeta:
    """Pagination metadata included in list responses."""
    page: int
    per_page: int
    total: int
    pages: int

    @staticmethod
    def create(page: int, per_page: int, total: int) -> "PaginationMeta":
        return PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            pages=ceil(total / per_page) if total > 0 else 1,
        )

    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "per_page": self.per_page,
            "total": self.total,
            "pages": self.pages,
        }


def build_response(
    data: list | dict,
    message: str = "Success",
    pagination: PaginationMeta | None = None,
) -> dict:
    """Build a standard API response envelope."""
    response: dict = {"success": True, "message": message, "data": data}
    if pagination:
        response["pagination"] = pagination.to_dict()
    return response


def build_error_response(message: str, error_code: str = "ERROR", details: dict | None = None) -> dict:
    """Build a standard error response envelope."""
    response: dict = {"success": False, "message": message, "error_code": error_code}
    if details:
        response["details"] = details
    return response
