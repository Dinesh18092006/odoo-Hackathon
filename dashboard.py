"""
AssetFlow — Dashboard KPIs, Notifications, Activity Logs, Reports
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional

from core.database import db_dep
from core.security import get_current_user, require_roles

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
mgr_or_admin = require_roles("Admin", "AssetManager", "DepartmentHead")


# ── Dashboard KPIs ─────────────────────────────────────────────────────────────
@router.get("/kpis")
def get_kpis(db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db

    cursor.execute("SELECT status, COUNT(*) AS cnt FROM assets GROUP BY status")
    status_counts = {r["status"]: r["cnt"] for r in cursor.fetchall()}

    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM maintenance_requests WHERE status IN ('Pending','Approved','InProgress')"
    )
    maintenance_today = cursor.fetchone()["cnt"]

    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM bookings WHERE status IN ('Upcoming','Ongoing')"
    )
    active_bookings = cursor.fetchone()["cnt"]

    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM transfer_requests WHERE status='Pending'"
    )
    pending_transfers = cursor.fetchone()["cnt"]

    cursor.execute("""
        SELECT COUNT(*) AS cnt FROM allocations
        WHERE status='Active'
          AND expected_return_date IS NOT NULL
          AND expected_return_date >= CURDATE()
          AND expected_return_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
    """)
    upcoming_returns = cursor.fetchone()["cnt"]

    cursor.execute("""
        SELECT COUNT(*) AS cnt FROM allocations
        WHERE status='Active'
          AND expected_return_date IS NOT NULL
          AND expected_return_date < CURDATE()
    """)
    overdue_returns = cursor.fetchone()["cnt"]

    # Overdue list
    cursor.execute("""
        SELECT al.id, a.asset_tag, a.name AS asset_name,
               e.name AS holder_name, al.expected_return_date
        FROM allocations al
        JOIN assets a ON a.id = al.asset_id
        LEFT JOIN employees e ON e.id = al.employee_id
        WHERE al.status='Active'
          AND al.expected_return_date < CURDATE()
        ORDER BY al.expected_return_date ASC
        LIMIT 10
    """)
    overdue_list = cursor.fetchall()

    return {
        "assets": {
            "available":        status_counts.get("Available", 0),
            "allocated":        status_counts.get("Allocated", 0),
            "reserved":         status_counts.get("Reserved", 0),
            "under_maintenance":status_counts.get("UnderMaintenance", 0),
            "lost":             status_counts.get("Lost", 0),
            "retired":          status_counts.get("Retired", 0),
            "disposed":         status_counts.get("Disposed", 0),
        },
        "maintenance_active":   maintenance_today,
        "active_bookings":      active_bookings,
        "pending_transfers":    pending_transfers,
        "upcoming_returns":     upcoming_returns,
        "overdue_returns":      overdue_returns,
        "overdue_list":         overdue_list,
    }


# ── Notifications ──────────────────────────────────────────────────────────────
@router.get("/notifications")
def get_notifications(db=Depends(db_dep), current=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("""
        SELECT * FROM notifications
        WHERE employee_id=%s
        ORDER BY created_at DESC
        LIMIT 50
    """, (current["id"],))
    return cursor.fetchall()


@router.patch("/notifications/{notif_id}/read")
def mark_read(notif_id: int, db=Depends(db_dep), current=Depends(get_current_user)):
    _, cursor = db
    cursor.execute(
        "UPDATE notifications SET is_read=1 WHERE id=%s AND employee_id=%s",
        (notif_id, current["id"]),
    )
    return {"message": "Marked as read"}


@router.patch("/notifications/read-all")
def mark_all_read(db=Depends(db_dep), current=Depends(get_current_user)):
    _, cursor = db
    cursor.execute(
        "UPDATE notifications SET is_read=1 WHERE employee_id=%s", (current["id"],)
    )
    return {"message": "All notifications marked as read"}


# ── Activity Logs ──────────────────────────────────────────────────────────────
@router.get("/logs")
def activity_logs(
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db=Depends(db_dep),
    _=Depends(mgr_or_admin),
):
    _, cursor = db
    cursor.execute("""
        SELECT al.*, e.name AS actor_name, e.role AS actor_role
        FROM activity_logs al
        LEFT JOIN employees e ON e.id = al.actor_id
        ORDER BY al.created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))
    return cursor.fetchall()


# ── Reports ────────────────────────────────────────────────────────────────────
@router.get("/reports/utilization")
def report_utilization(db=Depends(db_dep), _=Depends(mgr_or_admin)):
    """Asset utilization — allocation frequency per asset."""
    _, cursor = db
    cursor.execute("""
        SELECT a.asset_tag, a.name, a.status,
               c.name AS category,
               COUNT(al.id) AS allocation_count,
               SUM(DATEDIFF(COALESCE(al.returned_at, NOW()), al.allocated_at)) AS total_days_allocated
        FROM assets a
        LEFT JOIN asset_categories c ON c.id = a.category_id
        LEFT JOIN allocations al ON al.asset_id = a.id
        GROUP BY a.id, a.asset_tag, a.name, a.status, c.name
        ORDER BY allocation_count DESC
    """)
    return cursor.fetchall()


@router.get("/reports/maintenance")
def report_maintenance(db=Depends(db_dep), _=Depends(mgr_or_admin)):
    """Maintenance frequency by asset and category."""
    _, cursor = db
    cursor.execute("""
        SELECT a.asset_tag, a.name, c.name AS category,
               COUNT(mr.id) AS request_count,
               SUM(mr.status='Resolved') AS resolved_count
        FROM assets a
        JOIN asset_categories c ON c.id = a.category_id
        LEFT JOIN maintenance_requests mr ON mr.asset_id = a.id
        GROUP BY a.id ORDER BY request_count DESC
    """)
    return cursor.fetchall()


@router.get("/reports/department-allocation")
def report_dept_allocation(db=Depends(db_dep), _=Depends(mgr_or_admin)):
    """Assets per department."""
    _, cursor = db
    cursor.execute("""
        SELECT d.name AS department,
               COUNT(al.id) AS active_allocations,
               GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') AS asset_names
        FROM departments d
        LEFT JOIN allocations al ON al.department_id = d.id AND al.status='Active'
        LEFT JOIN assets a ON a.id = al.asset_id
        GROUP BY d.id ORDER BY active_allocations DESC
    """)
    return cursor.fetchall()


@router.get("/reports/booking-heatmap")
def report_booking_heatmap(db=Depends(db_dep), _=Depends(mgr_or_admin)):
    """Booking count by day-of-week and hour."""
    _, cursor = db
    cursor.execute("""
        SELECT
          DAYOFWEEK(start_time) AS dow,
          HOUR(start_time)      AS hour_slot,
          COUNT(*)              AS booking_count
        FROM bookings
        WHERE status != 'Cancelled'
        GROUP BY dow, hour_slot
        ORDER BY dow, hour_slot
    """)
    return cursor.fetchall()