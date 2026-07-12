"""
AssetFlow — Enterprise Asset & Resource Management System
FastAPI application entry point.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from config import settings
from database import create_all_tables
from utils.logger import logger
from utils.pagination import build_error_response
from routers import (
    auth_router, users_router, departments_router, categories_router,
    assets_router, allocations_router, transfers_router, bookings_router,
    maintenance_router, audits_router, notifications_router, logs_router,
    dashboard_router, reports_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} API...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Database: {settings.database_url}")

    # Create upload directories
    for sub_path in ["assets/images", "assets/documents", "qrcodes"]:
        os.makedirs(os.path.join(settings.upload_dir, sub_path), exist_ok=True)

    # Auto-create all database tables
    await create_all_tables()
    logger.info("Database tables created/verified successfully")
    logger.info(f"{settings.app_name} is ready — http://{settings.app_host}:{settings.app_port}")
    logger.info("Swagger UI: http://localhost:8000/docs")
    logger.info("=" * 60)

    yield

    logger.info(f"{settings.app_name} shutting down...")


# Create FastAPI app
app = FastAPI(
    title=f"{settings.app_name} API",
    description="""
## AssetFlow — Enterprise Asset & Resource Management System

A complete ERP platform for managing, monitoring, allocating, and maintaining
physical assets and shared resources.

### Key Features
- **Asset Lifecycle Management** — Available → Allocated → Under Maintenance → Retired
- **Resource Booking** — Calendar-based booking with conflict detection  
- **Asset Allocation** — Full approval workflow with history
- **Maintenance Workflow** — Raise → Approve → Assign → Resolve
- **Audit Workflow** — Audit cycles with discrepancy reports
- **Role-Based Access** — Admin, Asset Manager, Department Head, Employee

### Authentication
Use the `/api/v1/auth/login` endpoint to get a JWT token, then click
the **Authorize** button above and enter: `Bearer <your_token>`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== STATIC FILES ====================
# Serve uploaded files (images, documents, QR codes)
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler — returns structured error response."""
    from fastapi import HTTPException
    if isinstance(exc, HTTPException):
        detail = exc.detail
        if isinstance(detail, dict):
            return JSONResponse(
                status_code=exc.status_code,
                content=build_error_response(
                    detail.get("message", "An error occurred"),
                    detail.get("error_code", "ERROR"),
                ),
            )
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_response(str(detail)),
        )
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=build_error_response("An internal server error occurred", "INTERNAL_ERROR"),
    )


# ==================== REGISTER ROUTERS ====================
API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)
app.include_router(departments_router, prefix=API_PREFIX)
app.include_router(categories_router, prefix=API_PREFIX)
app.include_router(assets_router, prefix=API_PREFIX)
app.include_router(allocations_router, prefix=API_PREFIX)
app.include_router(transfers_router, prefix=API_PREFIX)
app.include_router(bookings_router, prefix=API_PREFIX)
app.include_router(maintenance_router, prefix=API_PREFIX)
app.include_router(audits_router, prefix=API_PREFIX)
app.include_router(notifications_router, prefix=API_PREFIX)
app.include_router(logs_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(reports_router, prefix=API_PREFIX)


# ==================== HEALTH CHECK ====================
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name, "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    """API root — redirects to docs."""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
