"""
AssetFlow — Audit Cycles
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from core.database import db_dep
from core.security import get_current_user, require_roles

router = APIRouter(prefix="/api/audits", tags=["audits"])
admin_only   = require_roles("Admin")
mgr_or_admin = require_roles("Admin", "AssetManager")


class AuditCycleIn(BaseModel):
    title: str
    scope_dept_id: Optional[int] = None
    scope_location: Optional[str] = None
    start_date: str
    end_date: str
    auditor_ids: List[int] = []


class AuditItemResultIn(BaseModel):
    result: str       # Verified | Missing | Damaged
    notes: Optional[str] = None


@router.get("/")
def list_cycles(db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("""
        SELECT ac.*, e.name AS created_by_name, d.name AS dept_name
        FROM audit_cycles ac
        JOIN employees e ON e.id = ac.created_by
        LEFT JOIN departments d ON d.id = ac.scope_dept_id
        ORDER BY ac.created_at DESC
    """)
    cycles = cursor.fetchall()
    for c in cycles:
        cursor.execute("""
            SELECT e.id, e.name FROM audit_auditors aa
            JOIN employees e ON e.id = aa.employee_id
            WHERE aa.audit_id=%s
        """, (c["id"],))
        c["auditors"] = cursor.fetchall()
    return cycles


@router.post("/", status_code=201)
def create_cycle(body: AuditCycleIn, db=Depends(db_dep), current=Depends(mgr_or_admin)):
    _, cursor = db
    cursor.execute("""
        INSERT INTO audit_cycles
          (title, scope_dept_id, scope_location, start_date, end_date, created_by)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (body.title, body.scope_dept_id, body.scope_location,
          body.start_date, body.end_date, current["id"]))
    cycle_id = cursor.lastrowid

    for aud_id in body.auditor_ids:
        cursor.execute(
            "INSERT IGNORE INTO audit_auditors (audit_id, employee_id) VALUES (%s,%s)",
            (cycle_id, aud_id),
        )

    # Auto-populate audit items from scope
    sql_assets = "SELECT id FROM assets WHERE status NOT IN ('Disposed','Retired')"
    params = []
    if body.scope_dept_id:
        sql_assets += """
            AND id IN (
                SELECT asset_id FROM allocations
                WHERE department_id=%s AND status='Active'
            )
        """
        params.append(body.scope_dept_id)
    if body.scope_location:
        sql_assets += " AND location LIKE %s"
        params.append(f"%{body.scope_location}%")
    cursor.execute(sql_assets, params)
    assets = cursor.fetchall()
    default_auditor = body.auditor_ids[0] if body.auditor_ids else current["id"]
    for asset in assets:
        cursor.execute(
            "INSERT INTO audit_items (audit_id, asset_id, auditor_id) VALUES (%s,%s,%s)",
            (cycle_id, asset["id"], default_auditor),
        )

    return {"id": cycle_id, "message": "Audit cycle created", "items_created": len(assets)}


@router.get("/{cycle_id}/items")
def get_cycle_items(cycle_id: int, db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("""
        SELECT ai.*, a.asset_tag, a.name AS asset_name, a.location,
               e.name AS auditor_name
        FROM audit_items ai
        JOIN assets a ON a.id = ai.asset_id
        JOIN employees e ON e.id = ai.auditor_id
        WHERE ai.audit_id=%s
        ORDER BY a.asset_tag
    """, (cycle_id,))
    return cursor.fetchall()


@router.patch("/{cycle_id}/items/{item_id}")
def mark_item(
    cycle_id: int, item_id: int,
    body: AuditItemResultIn,
    db=Depends(db_dep), current=Depends(get_current_user),
):
    _, cursor = db
    VALID = {"Verified", "Missing", "Damaged"}
    if body.result not in VALID:
        raise HTTPException(400, f"result must be one of {VALID}")
    cursor.execute(
        "UPDATE audit_items SET result=%s, notes=%s, checked_at=NOW() WHERE id=%s AND audit_id=%s",
        (body.result, body.notes, item_id, cycle_id),
    )
    return {"message": "Item marked"}


@router.get("/{cycle_id}/discrepancy-report")
def discrepancy_report(cycle_id: int, db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("""
        SELECT ai.*, a.asset_tag, a.name AS asset_name, a.location,
               a.serial_number, e.name AS auditor_name
        FROM audit_items ai
        JOIN assets a ON a.id = ai.asset_id
        JOIN employees e ON e.id = ai.auditor_id
        WHERE ai.audit_id=%s AND ai.result IN ('Missing','Damaged')
        ORDER BY ai.result, a.asset_tag
    """, (cycle_id,))
    return cursor.fetchall()


@router.patch("/{cycle_id}/close")
def close_cycle(cycle_id: int, db=Depends(db_dep), current=Depends(mgr_or_admin)):
    _, cursor = db
    cursor.execute("SELECT status FROM audit_cycles WHERE id=%s", (cycle_id,))
    cycle = cursor.fetchone()
    if not cycle:
        raise HTTPException(404, "Audit cycle not found")
    if cycle["status"] == "Closed":
        raise HTTPException(400, "Cycle already closed")

    # Mark confirmed-missing assets as Lost
    cursor.execute("""
        UPDATE assets SET status='Lost'
        WHERE id IN (
            SELECT asset_id FROM audit_items
            WHERE audit_id=%s AND result='Missing'
        )
    """, (cycle_id,))

    cursor.execute(
        "UPDATE audit_cycles SET status='Closed' WHERE id=%s", (cycle_id,)
    )
    _log(cursor, current["id"], "close_audit", "audit", cycle_id)
    return {"message": "Audit cycle closed. Missing assets marked as Lost."}


def _log(cursor, actor_id, action, entity_type, entity_id):
    cursor.execute(
        "INSERT INTO activity_logs (actor_id, action, entity_type, entity_id) VALUES (%s,%s,%s,%s)",
        (actor_id, action, entity_type, entity_id),
    )