"""
AssetFlow — Maintenance Request Workflow
Pending → Approved/Rejected → AssignedTechnician → InProgress → Resolved
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.database import db_dep
from core.security import get_current_user, require_roles

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])
mgr_or_admin = require_roles("Admin", "AssetManager")


class MaintenanceIn(BaseModel):
    asset_id: int
    description: str
    priority: str = "Medium"
    photo_url: Optional[str] = None


class ReviewIn(BaseModel):
    status: str          # Approved | Rejected
    technician_id: Optional[int] = None
    notes: Optional[str] = None


class ProgressIn(BaseModel):
    status: str          # InProgress | Resolved
    notes: Optional[str] = None


@router.get("/")
def list_requests(db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("""
        SELECT mr.*, a.asset_tag, a.name AS asset_name,
               rb.name AS raised_by_name, t.name AS technician_name,
               rv.name AS reviewed_by_name
        FROM maintenance_requests mr
        JOIN assets a ON a.id = mr.asset_id
        JOIN employees rb ON rb.id = mr.raised_by
        LEFT JOIN employees t  ON t.id  = mr.technician_id
        LEFT JOIN employees rv ON rv.id = mr.reviewed_by
        ORDER BY mr.created_at DESC
    """)
    return cursor.fetchall()


@router.post("/", status_code=201)
def raise_request(body: MaintenanceIn, db=Depends(db_dep), current=Depends(get_current_user)):
    _, cursor = db
    # Verify asset exists
    cursor.execute("SELECT id FROM assets WHERE id=%s", (body.asset_id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Asset not found")

    VALID_PRI = {"Low", "Medium", "High", "Critical"}
    if body.priority not in VALID_PRI:
        raise HTTPException(400, f"Priority must be one of {VALID_PRI}")

    cursor.execute("""
        INSERT INTO maintenance_requests
          (asset_id, raised_by, description, priority, photo_url)
        VALUES (%s,%s,%s,%s,%s)
    """, (body.asset_id, current["id"], body.description, body.priority, body.photo_url))

    _log(cursor, current["id"], "raise_maintenance", "asset", body.asset_id)
    return {"id": cursor.lastrowid, "message": "Maintenance request submitted"}


@router.patch("/{req_id}/review")
def review_request(req_id: int, body: ReviewIn, db=Depends(db_dep), current=Depends(mgr_or_admin)):
    _, cursor = db
    cursor.execute(
        "SELECT * FROM maintenance_requests WHERE id=%s AND status='Pending'",
        (req_id,),
    )
    req = cursor.fetchone()
    if not req:
        raise HTTPException(404, "Pending maintenance request not found")

    if body.status == "Approved":
        cursor.execute("""
            UPDATE maintenance_requests
            SET status='Approved', reviewed_by=%s, reviewed_at=NOW(),
                technician_id=%s, notes=%s
            WHERE id=%s
        """, (current["id"], body.technician_id, body.notes, req_id))
        # Asset flips to UnderMaintenance
        cursor.execute(
            "UPDATE assets SET status='UnderMaintenance' WHERE id=%s", (req["asset_id"],)
        )
        if body.technician_id:
            _notify(cursor, body.technician_id,
                    "Maintenance Assigned",
                    f"You have been assigned to a maintenance task.",
                    "maintenance")
    elif body.status == "Rejected":
        cursor.execute("""
            UPDATE maintenance_requests
            SET status='Rejected', reviewed_by=%s, reviewed_at=NOW(), notes=%s
            WHERE id=%s
        """, (current["id"], body.notes, req_id))
        _notify(cursor, req["raised_by"],
                "Maintenance Request Rejected",
                f"Your maintenance request was rejected. Note: {body.notes or 'N/A'}",
                "maintenance")
    else:
        raise HTTPException(400, "status must be 'Approved' or 'Rejected'")

    _log(cursor, current["id"], f"maintenance_{body.status.lower()}", "maintenance", req_id)
    return {"message": f"Request {body.status}"}


@router.patch("/{req_id}/progress")
def update_progress(req_id: int, body: ProgressIn, db=Depends(db_dep), current=Depends(get_current_user)):
    _, cursor = db
    cursor.execute(
        "SELECT * FROM maintenance_requests WHERE id=%s", (req_id,)
    )
    req = cursor.fetchone()
    if not req:
        raise HTTPException(404, "Request not found")

    VALID = {"AssignedTechnician", "InProgress", "Resolved"}
    if body.status not in VALID:
        raise HTTPException(400, f"Status must be one of: {', '.join(VALID)}")

    if body.status == "Resolved":
        cursor.execute(
            "UPDATE maintenance_requests SET status='Resolved', resolved_at=NOW(), notes=%s WHERE id=%s",
            (body.notes, req_id),
        )
        cursor.execute(
            "UPDATE assets SET status='Available' WHERE id=%s", (req["asset_id"],)
        )
        _notify(cursor, req["raised_by"],
                "Maintenance Resolved",
                "Your asset's maintenance is complete and it's now Available.",
                "maintenance")
    else:
        cursor.execute(
            "UPDATE maintenance_requests SET status=%s, notes=%s WHERE id=%s",
            (body.status, body.notes, req_id),
        )

    _log(cursor, current["id"], f"maintenance_{body.status.lower()}", "maintenance", req_id)
    return {"message": f"Status updated to {body.status}"}


def _notify(cursor, emp_id, title, body_text, ntype):
    if not emp_id:
        return
    cursor.execute(
        "INSERT INTO notifications (employee_id, title, body, type) VALUES (%s,%s,%s,%s)",
        (emp_id, title, body_text, ntype),
    )


def _log(cursor, actor_id, action, entity_type, entity_id):
    cursor.execute(
        "INSERT INTO activity_logs (actor_id, action, entity_type, entity_id) VALUES (%s,%s,%s,%s)",
        (actor_id, action, entity_type, entity_id),
    )