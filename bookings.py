"""
AssetFlow — Resource Booking with overlap validation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from core.database import db_dep
from core.security import get_current_user

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


class BookingIn(BaseModel):
    asset_id: int
    start_time: str    # ISO datetime string
    end_time: str
    purpose: Optional[str] = None


class RescheduleIn(BaseModel):
    start_time: str
    end_time: str


@router.get("/")
def list_bookings(
    asset_id: Optional[int] = Query(None),
    db=Depends(db_dep),
    current=Depends(get_current_user),
):
    _, cursor = db
    sql = """
        SELECT b.*, a.asset_tag, a.name AS asset_name, e.name AS booked_by_name
        FROM bookings b
        JOIN assets a ON a.id = b.asset_id
        JOIN employees e ON e.id = b.booked_by
        WHERE 1=1
    """
    params = []
    if asset_id:
        sql += " AND b.asset_id = %s"
        params.append(asset_id)
    sql += " ORDER BY b.start_time DESC"
    cursor.execute(sql, params)
    return cursor.fetchall()


@router.post("/", status_code=201)
def create_booking(body: BookingIn, db=Depends(db_dep), current=Depends(get_current_user)):
    _, cursor = db

    # Verify asset is bookable
    cursor.execute("SELECT id, name, is_bookable, status FROM assets WHERE id=%s", (body.asset_id,))
    asset = cursor.fetchone()
    if not asset:
        raise HTTPException(404, "Asset not found")
    if not asset["is_bookable"]:
        raise HTTPException(400, "This asset is not marked as bookable/shared")

    # Overlap validation
    cursor.execute("""
        SELECT id, start_time, end_time, booked_by FROM bookings
        WHERE asset_id = %s
          AND status IN ('Upcoming','Ongoing')
          AND start_time < %s
          AND end_time   > %s
    """, (body.asset_id, body.end_time, body.start_time))
    overlap = cursor.fetchone()
    if overlap:
        raise HTTPException(409, {
            "detail": "Time slot overlaps with an existing booking",
            "conflict_start": str(overlap["start_time"]),
            "conflict_end": str(overlap["end_time"]),
        })

    cursor.execute("""
        INSERT INTO bookings (asset_id, booked_by, start_time, end_time, purpose)
        VALUES (%s,%s,%s,%s,%s)
    """, (body.asset_id, current["id"], body.start_time, body.end_time, body.purpose))

    # Mark asset Reserved if Available
    cursor.execute(
        "UPDATE assets SET status='Reserved' WHERE id=%s AND status='Available'",
        (body.asset_id,),
    )

    _log(cursor, current["id"], "book_resource", "asset", body.asset_id)
    return {"id": cursor.lastrowid, "message": "Booking confirmed"}


@router.patch("/{booking_id}/cancel")
def cancel_booking(booking_id: int, db=Depends(db_dep), current=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("SELECT * FROM bookings WHERE id=%s", (booking_id,))
    b = cursor.fetchone()
    if not b:
        raise HTTPException(404, "Booking not found")
    if b["booked_by"] != current["id"] and current["role"] not in ("Admin", "AssetManager"):
        raise HTTPException(403, "Not authorised to cancel this booking")
    cursor.execute("UPDATE bookings SET status='Cancelled' WHERE id=%s", (booking_id,))
    # Revert asset to Available if no other upcoming booking
    cursor.execute("""
        SELECT id FROM bookings WHERE asset_id=%s AND status IN ('Upcoming','Ongoing')
    """, (b["asset_id"],))
    if not cursor.fetchone():
        cursor.execute(
            "UPDATE assets SET status='Available' WHERE id=%s AND status='Reserved'",
            (b["asset_id"],),
        )
    return {"message": "Booking cancelled"}


@router.patch("/{booking_id}/reschedule")
def reschedule_booking(
    booking_id: int, body: RescheduleIn,
    db=Depends(db_dep), current=Depends(get_current_user),
):
    _, cursor = db
    cursor.execute("SELECT * FROM bookings WHERE id=%s AND status='Upcoming'", (booking_id,))
    b = cursor.fetchone()
    if not b:
        raise HTTPException(404, "Upcoming booking not found")
    if b["booked_by"] != current["id"] and current["role"] not in ("Admin", "AssetManager"):
        raise HTTPException(403, "Not authorised")

    # Overlap check (exclude self)
    cursor.execute("""
        SELECT id FROM bookings
        WHERE asset_id=%s AND status IN ('Upcoming','Ongoing')
          AND id != %s AND start_time < %s AND end_time > %s
    """, (b["asset_id"], booking_id, body.end_time, body.start_time))
    if cursor.fetchone():
        raise HTTPException(409, "New time slot overlaps with another booking")

    cursor.execute(
        "UPDATE bookings SET start_time=%s, end_time=%s WHERE id=%s",
        (body.start_time, body.end_time, booking_id),
    )
    return {"message": "Booking rescheduled"}


def _log(cursor, actor_id, action, entity_type, entity_id):
    cursor.execute(
        "INSERT INTO activity_logs (actor_id, action, entity_type, entity_id) VALUES (%s,%s,%s,%s)",
        (actor_id, action, entity_type, entity_id),
    )