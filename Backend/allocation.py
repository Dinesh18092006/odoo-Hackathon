"""
AssetFlow — Asset Allocation, Transfer & Return
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from core.database import db_dep
from core.security import get_current_user, require_roles

router = APIRouter(prefix="/api/allocations", tags=["allocations"])
mgr_or_admin   = require_roles("Admin", "AssetManager")
head_mgr_admin = require_roles("Admin", "AssetManager", "DepartmentHead")


# ── Schemas ────────────────────────────────────────────────────────────────────
class AllocateIn(BaseModel):
    asset_id: int
    employee_id: Optional[int] = None
    department_id: Optional[int] = None
    expected_return_date: Optional[str] = None


class ReturnIn(BaseModel):
    allocation_id: int
    condition_checkin: Optional[str] = None


class TransferIn(BaseModel):
    asset_id: int
    to_employee_id: Optional[int] = None
    reason: Optional[str] = None


class ReviewIn(BaseModel):
    status: str   # Approved | Rejected


# ── Allocation ─────────────────────────────────────────────────────────────────
@router.get("/")
def list_allocations(db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("""
        SELECT al.*, a.asset_tag, a.name AS asset_name,
               e.name  AS employee_name, d.name AS dept_name,
               ab.name AS allocated_by_name
        FROM allocations al
        JOIN assets a ON a.id = al.asset_id
        LEFT JOIN employees e  ON e.id  = al.employee_id
        LEFT JOIN departments d ON d.id = al.department_id
        LEFT JOIN employees ab ON ab.id = al.allocated_by
        ORDER BY al.allocated_at DESC
    """)
    rows = cursor.fetchall()
    now = datetime.now(timezone.utc).date()
    for r in rows:
        if r["status"] == "Active" and r.get("expected_return_date"):
            exp = r["expected_return_date"]
            if hasattr(exp, "date"):
                exp = exp.date()
            if exp < now:
                r["is_overdue"] = True
    return rows


@router.post("/", status_code=201)
def allocate_asset(body: AllocateIn, db=Depends(db_dep), current=Depends(mgr_or_admin)):
    _, cursor = db

    # Conflict check
    cursor.execute(
        "SELECT id FROM allocations WHERE asset_id=%s AND status='Active'",
        (body.asset_id,),
    )
    if cursor.fetchone():
        cursor.execute("""
            SELECT e.name AS holder_name FROM allocations al
            LEFT JOIN employees e ON e.id = al.employee_id
            WHERE al.asset_id=%s AND al.status='Active'
        """, (body.asset_id,))
        holder = cursor.fetchone()
        raise HTTPException(409, {
            "detail": "Asset already allocated",
            "held_by": holder["holder_name"] if holder else "another user",
        })

    # Check asset availability
    cursor.execute("SELECT status FROM assets WHERE id=%s", (body.asset_id,))
    asset = cursor.fetchone()
    if not asset or asset["status"] not in ("Available",):
        raise HTTPException(400, f"Asset is not available (status: {asset['status'] if asset else 'unknown'})")

    cursor.execute("""
        INSERT INTO allocations
          (asset_id, employee_id, department_id, allocated_by, expected_return_date)
        VALUES (%s,%s,%s,%s,%s)
    """, (body.asset_id, body.employee_id, body.department_id,
          current["id"], body.expected_return_date))
    cursor.execute("UPDATE assets SET status='Allocated' WHERE id=%s", (body.asset_id,))

    _notify(cursor, body.employee_id,
            "Asset Allocated",
            f"An asset has been allocated to you.",
            "allocation")
    _log(cursor, current["id"], "allocate_asset", "asset", body.asset_id)
    return {"message": "Asset allocated successfully"}


@router.post("/return")
def return_asset(body: ReturnIn, db=Depends(db_dep), current=Depends(mgr_or_admin)):
    _, cursor = db
    cursor.execute("SELECT * FROM allocations WHERE id=%s AND status='Active'", (body.allocation_id,))
    alloc = cursor.fetchone()
    if not alloc:
        raise HTTPException(404, "Active allocation not found")

    cursor.execute(
        "UPDATE allocations SET returned_at=NOW(), condition_checkin=%s, status='Returned' WHERE id=%s",
        (body.condition_checkin, body.allocation_id),
    )
    cursor.execute("UPDATE assets SET status='Available' WHERE id=%s", (alloc["asset_id"],))
    _log(cursor, current["id"], "return_asset", "asset", alloc["asset_id"])
    return {"message": "Asset returned and marked Available"}


# ── Transfer Requests ──────────────────────────────────────────────────────────
@router.get("/transfers")
def list_transfers(db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("""
        SELECT tr.*, a.asset_tag, a.name AS asset_name,
               rb.name AS requested_by_name,
               fe.name AS from_employee_name,
               te.name AS to_employee_name
        FROM transfer_requests tr
        JOIN assets a ON a.id = tr.asset_id
        LEFT JOIN employees rb ON rb.id = tr.requested_by
        LEFT JOIN employees fe ON fe.id = tr.from_employee
        LEFT JOIN employees te ON te.id = tr.to_employee
        ORDER BY tr.created_at DESC
    """)
    return cursor.fetchall()


@router.post("/transfers", status_code=201)
def raise_transfer(body: TransferIn, db=Depends(db_dep), current=Depends(get_current_user)):
    _, cursor = db
    cursor.execute(
        "SELECT employee_id FROM allocations WHERE asset_id=%s AND status='Active'",
        (body.asset_id,),
    )
    alloc = cursor.fetchone()
    cursor.execute("""
        INSERT INTO transfer_requests
          (asset_id, requested_by, from_employee, to_employee, reason)
        VALUES (%s,%s,%s,%s,%s)
    """, (body.asset_id, current["id"],
          alloc["employee_id"] if alloc else None,
          body.to_employee_id, body.reason))
    _log(cursor, current["id"], "request_transfer", "asset", body.asset_id)
    return {"message": "Transfer request submitted"}


@router.patch("/transfers/{tr_id}/review")
def review_transfer(tr_id: int, body: ReviewIn, db=Depends(db_dep), current=Depends(head_mgr_admin)):
    _, cursor = db
    cursor.execute("SELECT * FROM transfer_requests WHERE id=%s AND status='Pending'", (tr_id,))
    tr = cursor.fetchone()
    if not tr:
        raise HTTPException(404, "Pending transfer request not found")

    cursor.execute(
        "UPDATE transfer_requests SET status=%s, reviewed_by=%s, reviewed_at=NOW() WHERE id=%s",
        (body.status, current["id"], tr_id),
    )

    if body.status == "Approved":
        # Close old allocation
        cursor.execute(
            "UPDATE allocations SET status='Returned', returned_at=NOW() WHERE asset_id=%s AND status='Active'",
            (tr["asset_id"],),
        )
        # Create new allocation
        cursor.execute("""
            INSERT INTO allocations (asset_id, employee_id, allocated_by)
            VALUES (%s,%s,%s)
        """, (tr["asset_id"], tr["to_employee"], current["id"]))
        _notify(cursor, tr["to_employee"], "Transfer Approved",
                "An asset transfer to you has been approved.", "transfer")

    _log(cursor, current["id"], f"transfer_{body.status.lower()}", "transfer", tr_id)
    return {"message": f"Transfer {body.status}"}


# ── Helpers ────────────────────────────────────────────────────────────────────
def _notify(cursor, employee_id, title, body_text, ntype):
    if not employee_id:
        return
    cursor.execute(
        "INSERT INTO notifications (employee_id, title, body, type) VALUES (%s,%s,%s,%s)",
        (employee_id, title, body_text, ntype),
    )


def _log(cursor, actor_id, action, entity_type, entity_id, details=None):
    import json
    cursor.execute(
        "INSERT INTO activity_logs (actor_id, action, entity_type, entity_id, details) VALUES (%s,%s,%s,%s,%s)",
        (actor_id, action, entity_type, entity_id, json.dumps(details) if details else None),
    )