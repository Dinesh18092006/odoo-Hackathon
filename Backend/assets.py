"""
AssetFlow — Asset Registration & Directory
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import json

from core.database import db_dep
from core.security import get_current_user, require_roles

router = APIRouter(prefix="/api/assets", tags=["assets"])
mgr_or_admin = require_roles("Admin", "AssetManager")


# ── Helpers ────────────────────────────────────────────────────────────────────
def _next_asset_tag(cursor) -> str:
    cursor.execute("INSERT INTO asset_tag_seq () VALUES ()")
    seq_id = cursor.lastrowid
    return f"AF-{seq_id:04d}"


# ── Schemas ────────────────────────────────────────────────────────────────────
class AssetIn(BaseModel):
    name: str
    category_id: int
    serial_number: Optional[str] = None
    acquisition_date: Optional[str] = None
    acquisition_cost: Optional[float] = None
    condition: str = "New"
    location: Optional[str] = None
    is_bookable: bool = False
    photo_url: Optional[str] = None
    documents_url: Optional[str] = None
    extra_data: Optional[dict] = None


class AssetStatusIn(BaseModel):
    status: str


# ── Routes ─────────────────────────────────────────────────────────────────────
@router.get("/")
def list_assets(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    is_bookable: Optional[bool] = Query(None),
    db=Depends(db_dep),
    _=Depends(get_current_user),
):
    _, cursor = db
    sql = """
        SELECT a.*, c.name AS category_name,
               al.employee_id AS current_holder_id,
               e.name AS current_holder_name,
               al.department_id AS current_dept_id,
               d.name AS current_dept_name
        FROM assets a
        LEFT JOIN asset_categories c ON c.id = a.category_id
        LEFT JOIN allocations al ON al.asset_id = a.id AND al.status = 'Active'
        LEFT JOIN employees e ON e.id = al.employee_id
        LEFT JOIN departments d ON d.id = al.department_id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (a.asset_tag LIKE %s OR a.name LIKE %s OR a.serial_number LIKE %s)"
        p = f"%{search}%"
        params += [p, p, p]
    if category_id:
        sql += " AND a.category_id = %s"
        params.append(category_id)
    if status:
        sql += " AND a.status = %s"
        params.append(status)
    if location:
        sql += " AND a.location LIKE %s"
        params.append(f"%{location}%")
    if is_bookable is not None:
        sql += " AND a.is_bookable = %s"
        params.append(1 if is_bookable else 0)
    sql += " ORDER BY a.id DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    for r in rows:
        if r.get("extra_data") and isinstance(r["extra_data"], str):
            r["extra_data"] = json.loads(r["extra_data"])
    return rows


@router.get("/{asset_id}")
def get_asset(asset_id: int, db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("""
        SELECT a.*, c.name AS category_name
        FROM assets a
        LEFT JOIN asset_categories c ON c.id = a.category_id
        WHERE a.id = %s
    """, (asset_id,))
    asset = cursor.fetchone()
    if not asset:
        raise HTTPException(404, "Asset not found")
    if asset.get("extra_data") and isinstance(asset["extra_data"], str):
        asset["extra_data"] = json.loads(asset["extra_data"])

    # Allocation history
    cursor.execute("""
        SELECT al.*, e.name AS employee_name, d.name AS dept_name,
               ab.name AS allocated_by_name
        FROM allocations al
        LEFT JOIN employees e  ON e.id  = al.employee_id
        LEFT JOIN departments d ON d.id = al.department_id
        LEFT JOIN employees ab ON ab.id = al.allocated_by
        WHERE al.asset_id = %s ORDER BY al.allocated_at DESC
    """, (asset_id,))
    asset["allocation_history"] = cursor.fetchall()

    # Maintenance history
    cursor.execute("""
        SELECT mr.*, e.name AS raised_by_name, t.name AS technician_name
        FROM maintenance_requests mr
        LEFT JOIN employees e ON e.id = mr.raised_by
        LEFT JOIN employees t ON t.id = mr.technician_id
        WHERE mr.asset_id = %s ORDER BY mr.created_at DESC
    """, (asset_id,))
    asset["maintenance_history"] = cursor.fetchall()

    return asset


@router.post("/", status_code=201)
def create_asset(body: AssetIn, db=Depends(db_dep), _=Depends(mgr_or_admin)):
    _, cursor = db
    tag = _next_asset_tag(cursor)
    cursor.execute("""
        INSERT INTO assets
          (asset_tag, name, category_id, serial_number, acquisition_date,
           acquisition_cost, `condition`, location, is_bookable,
           photo_url, documents_url, extra_data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        tag, body.name, body.category_id, body.serial_number,
        body.acquisition_date, body.acquisition_cost, body.condition,
        body.location, 1 if body.is_bookable else 0,
        body.photo_url, body.documents_url,
        json.dumps(body.extra_data) if body.extra_data else None,
    ))
    return {"id": cursor.lastrowid, "asset_tag": tag, "message": "Asset registered"}


@router.put("/{asset_id}")
def update_asset(asset_id: int, body: AssetIn, db=Depends(db_dep), _=Depends(mgr_or_admin)):
    _, cursor = db
    cursor.execute("""
        UPDATE assets SET
          name=%s, category_id=%s, serial_number=%s, acquisition_date=%s,
          acquisition_cost=%s, `condition`=%s, location=%s, is_bookable=%s,
          photo_url=%s, documents_url=%s, extra_data=%s
        WHERE id=%s
    """, (
        body.name, body.category_id, body.serial_number, body.acquisition_date,
        body.acquisition_cost, body.condition, body.location,
        1 if body.is_bookable else 0, body.photo_url, body.documents_url,
        json.dumps(body.extra_data) if body.extra_data else None,
        asset_id,
    ))
    return {"message": "Asset updated"}


@router.patch("/{asset_id}/status")
def update_status(asset_id: int, body: AssetStatusIn, db=Depends(db_dep), _=Depends(mgr_or_admin)):
    VALID = {"Available","Allocated","Reserved","UnderMaintenance","Lost","Retired","Disposed"}
    if body.status not in VALID:
        raise HTTPException(400, f"Invalid status. Use: {', '.join(VALID)}")
    _, cursor = db
    cursor.execute("UPDATE assets SET status=%s WHERE id=%s", (body.status, asset_id))
    return {"message": "Status updated"}