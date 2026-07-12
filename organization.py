"""
AssetFlow — Organization Setup (Admin only)
Departments, Asset Categories, Employee Directory
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Any
import json

from core.database import db_dep
from core.security import get_current_user, require_roles, hash_password

router = APIRouter(prefix="/api/org", tags=["organization"])

admin_only   = require_roles("Admin")
mgr_or_admin = require_roles("Admin", "AssetManager")


# ══════════════════════════════════════════════════════════════════════
# DEPARTMENTS
# ══════════════════════════════════════════════════════════════════════
class DeptIn(BaseModel):
    name: str
    parent_id: Optional[int] = None
    head_id: Optional[int] = None
    status: str = "Active"


@router.get("/departments")
def list_departments(db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("""
        SELECT d.*, e.name AS head_name, p.name AS parent_name
        FROM departments d
        LEFT JOIN employees e ON e.id = d.head_id
        LEFT JOIN departments p ON p.id = d.parent_id
        ORDER BY d.name
    """)
    return cursor.fetchall()


@router.post("/departments", status_code=201)
def create_department(body: DeptIn, db=Depends(db_dep), _=Depends(admin_only)):
    _, cursor = db
    cursor.execute(
        "INSERT INTO departments (name, parent_id, head_id, status) VALUES (%s,%s,%s,%s)",
        (body.name, body.parent_id, body.head_id, body.status),
    )
    return {"id": cursor.lastrowid, "message": "Department created"}


@router.put("/departments/{dept_id}")
def update_department(dept_id: int, body: DeptIn, db=Depends(db_dep), _=Depends(admin_only)):
    _, cursor = db
    cursor.execute(
        "UPDATE departments SET name=%s, parent_id=%s, head_id=%s, status=%s WHERE id=%s",
        (body.name, body.parent_id, body.head_id, body.status, dept_id),
    )
    return {"message": "Department updated"}


# ══════════════════════════════════════════════════════════════════════
# ASSET CATEGORIES
# ══════════════════════════════════════════════════════════════════════
class CategoryIn(BaseModel):
    name: str
    extra_fields: Optional[dict] = None


@router.get("/categories")
def list_categories(db=Depends(db_dep), _=Depends(get_current_user)):
    _, cursor = db
    cursor.execute("SELECT * FROM asset_categories ORDER BY name")
    rows = cursor.fetchall()
    for r in rows:
        if r.get("extra_fields") and isinstance(r["extra_fields"], str):
            r["extra_fields"] = json.loads(r["extra_fields"])
    return rows


@router.post("/categories", status_code=201)
def create_category(body: CategoryIn, db=Depends(db_dep), _=Depends(admin_only)):
    _, cursor = db
    cursor.execute(
        "INSERT INTO asset_categories (name, extra_fields) VALUES (%s,%s)",
        (body.name, json.dumps(body.extra_fields) if body.extra_fields else None),
    )
    return {"id": cursor.lastrowid, "message": "Category created"}


@router.put("/categories/{cat_id}")
def update_category(cat_id: int, body: CategoryIn, db=Depends(db_dep), _=Depends(admin_only)):
    _, cursor = db
    cursor.execute(
        "UPDATE asset_categories SET name=%s, extra_fields=%s WHERE id=%s",
        (body.name, json.dumps(body.extra_fields) if body.extra_fields else None, cat_id),
    )
    return {"message": "Category updated"}


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int, db=Depends(db_dep), _=Depends(admin_only)):
    _, cursor = db
    cursor.execute("DELETE FROM asset_categories WHERE id=%s", (cat_id,))
    return {"message": "Category deleted"}


# ══════════════════════════════════════════════════════════════════════
# EMPLOYEES
# ══════════════════════════════════════════════════════════════════════
class EmployeeCreateIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    department_id: Optional[int] = None
    status: str = "Active"


class EmployeeUpdateIn(BaseModel):
    name: str
    department_id: Optional[int] = None
    role: Optional[str] = None
    status: str = "Active"


@router.get("/employees")
def list_employees(db=Depends(db_dep), _=Depends(mgr_or_admin)):
    _, cursor = db
    cursor.execute("""
        SELECT e.id, e.name, e.email, e.role, e.status,
               e.department_id, d.name AS department_name, e.created_at
        FROM employees e
        LEFT JOIN departments d ON d.id = e.department_id
        ORDER BY e.name
    """)
    return cursor.fetchall()


@router.get("/employees/all")
def list_all_employees(db=Depends(db_dep), _=Depends(get_current_user)):
    """Lightweight list for dropdowns."""
    _, cursor = db
    cursor.execute("SELECT id, name, email, role, department_id FROM employees WHERE status='Active' ORDER BY name")
    return cursor.fetchall()


@router.post("/employees", status_code=201)
def create_employee(body: EmployeeCreateIn, db=Depends(db_dep), _=Depends(admin_only)):
    _, cursor = db
    cursor.execute("SELECT id FROM employees WHERE email=%s", (body.email,))
    if cursor.fetchone():
        raise HTTPException(400, "Email already in use")
    cursor.execute(
        "INSERT INTO employees (name, email, password_hash, department_id, status) VALUES (%s,%s,%s,%s,%s)",
        (body.name, body.email, hash_password(body.password), body.department_id, body.status),
    )
    return {"id": cursor.lastrowid, "message": "Employee created"}


@router.put("/employees/{emp_id}")
def update_employee(emp_id: int, body: EmployeeUpdateIn, db=Depends(db_dep), _=Depends(admin_only)):
    _, cursor = db
    VALID_ROLES = {"Admin", "AssetManager", "DepartmentHead", "Employee"}
    if body.role and body.role not in VALID_ROLES:
        raise HTTPException(400, f"Invalid role: {body.role}")
    if body.role:
        cursor.execute(
            "UPDATE employees SET name=%s, department_id=%s, role=%s, status=%s WHERE id=%s",
            (body.name, body.department_id, body.role, body.status, emp_id),
        )
    else:
        cursor.execute(
            "UPDATE employees SET name=%s, department_id=%s, status=%s WHERE id=%s",
            (body.name, body.department_id, body.status, emp_id),
        )
    return {"message": "Employee updated"}