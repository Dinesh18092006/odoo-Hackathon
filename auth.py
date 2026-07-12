"""
AssetFlow — Authentication routes
POST /api/auth/signup
POST /api/auth/login
POST /api/auth/forgot-password
POST /api/auth/reset-password
GET  /api/auth/me
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
import secrets

from core.database import db_dep
from core.security import (
    hash_password, verify_password,
    create_access_token, get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Schemas ────────────────────────────────────────────────────────────────────
class SignupIn(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ForgotIn(BaseModel):
    email: EmailStr


class ResetIn(BaseModel):
    token: str
    new_password: str


# ── Routes ─────────────────────────────────────────────────────────────────────
@router.post("/signup", status_code=201)
def signup(body: SignupIn, db=Depends(db_dep)):
    conn, cursor = db
    cursor.execute("SELECT id FROM employees WHERE email=%s", (body.email,))
    if cursor.fetchone():
        raise HTTPException(400, "Email already registered")
    cursor.execute(
        "INSERT INTO employees (name, email, password_hash, role) VALUES (%s,%s,%s,'Employee')",
        (body.name, body.email, hash_password(body.password)),
    )
    return {"message": "Account created. You can now log in."}


@router.post("/login")
def login(body: LoginIn, db=Depends(db_dep)):
    conn, cursor = db
    cursor.execute(
        "SELECT id, name, email, role, password_hash, status FROM employees WHERE email=%s",
        (body.email,),
    )
    user = cursor.fetchone()
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    if user["status"] != "Active":
        raise HTTPException(403, "Account is inactive. Contact your administrator.")

    token = create_access_token({"sub": user["id"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        },
    }


@router.post("/forgot-password")
def forgot_password(body: ForgotIn, db=Depends(db_dep)):
    conn, cursor = db
    cursor.execute("SELECT id FROM employees WHERE email=%s", (body.email,))
    user = cursor.fetchone()
    if not user:
        # Don't reveal existence
        return {"message": "If that email exists, a reset link has been sent."}
    token = secrets.token_urlsafe(32)
    exp = datetime.now(timezone.utc) + timedelta(hours=1)
    cursor.execute(
        "UPDATE employees SET reset_token=%s, reset_token_exp=%s WHERE id=%s",
        (token, exp, user["id"]),
    )
    # In production: send email with token. Here we return it for demo.
    return {"message": "Reset token generated.", "reset_token": token}


@router.post("/reset-password")
def reset_password(body: ResetIn, db=Depends(db_dep)):
    conn, cursor = db
    cursor.execute(
        "SELECT id, reset_token_exp FROM employees WHERE reset_token=%s",
        (body.token,),
    )
    user = cursor.fetchone()
    if not user:
        raise HTTPException(400, "Invalid reset token")
    if user["reset_token_exp"] < datetime.now(timezone.utc):
        raise HTTPException(400, "Reset token has expired")
    cursor.execute(
        "UPDATE employees SET password_hash=%s, reset_token=NULL, reset_token_exp=NULL WHERE id=%s",
        (hash_password(body.new_password), user["id"]),
    )
    return {"message": "Password updated. You can now log in."}


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user