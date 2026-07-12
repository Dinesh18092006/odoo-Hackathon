"""
AssetFlow — FastAPI Application Entry Point
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routers import auth, organization, assets, allocations, bookings, maintenance, audits, dashboard

app = FastAPI(
    title="AssetFlow API",
    description="Enterprise Asset & Resource Management System",
    version="1.0.0",
)

# ── CORS (adjust origins in production) ──────────────────────────────────────
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5500")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://127.0.0.1:5500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static uploads ────────────────────────────────────────────────────────────
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(organization.router)
app.include_router(assets.router)
app.include_router(allocations.router)
app.include_router(bookings.router)
app.include_router(maintenance.router)
app.include_router(audits.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "AssetFlow API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}