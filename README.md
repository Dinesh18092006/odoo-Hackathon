# AssetFlow — Enterprise Asset & Resource Management System

> **Production-Grade ERP Platform** | FastAPI · PostgreSQL · Vanilla JS · SQLAlchemy · JWT

---

## Table of Contents

1. [Project Vision](#project-vision)
2. [Tech Stack](#tech-stack)
3. [UI Design System](#ui-design-system)
4. [Project Structure](#project-structure)
5. [Database Design](#database-design)
6. [Authentication & RBAC](#authentication--rbac)
7. [Modules](#modules)
8. [Asset Lifecycle](#asset-lifecycle)
9. [Business Rules](#business-rules)
10. [API Design](#api-design)
11. [Security](#security)
12. [Search, Filters & Pagination](#search-filters--pagination)
13. [Notifications](#notifications)
14. [Reports & Analytics](#reports--analytics)
15. [Logging & Audit Trail](#logging--audit-trail)
16. [Development Phases](#development-phases)
17. [Coding Standards](#coding-standards)
18. [Team Roles](#team-roles)

---

## Project Vision

**AssetFlow** is a centralized enterprise ERP platform built to help organizations manage, monitor, allocate, and maintain physical assets and shared resources efficiently.

The system eliminates spreadsheets and manual tracking by providing a unified, role-based, workflow-driven platform for the complete lifecycle of every asset in an organization.

### Core Capabilities

| Capability | Description |
|---|---|
| **Asset Lifecycle Management** | Track every asset from procurement to disposal |
| **Resource Booking** | Calendar-based booking with conflict detection |
| **Asset Allocation** | Allocate, transfer, and return assets with approval workflows |
| **Maintenance Workflow** | Raise, assign, track and resolve maintenance requests |
| **Audit Workflow** | Scheduled audits, discrepancy reports, auditor assignments |
| **Notifications** | Real-time event-driven notifications |
| **Analytics & Reports** | KPI dashboards, charts, CSV/PDF exports |
| **Activity Logs** | Complete, immutable audit trail of every user action |
| **Role-Based Access Control** | Granular permissions per user role |

---

## Tech Stack

### Frontend
| Layer | Technology |
|---|---|
| Markup | HTML5 (Semantic) |
| Styling | CSS3 (Vanilla, Custom Design System) |
| Logic | JavaScript ES6+ (Vanilla, Modular) |

### Backend
| Layer | Technology |
|---|---|
| Framework | FastAPI (Python 3.11+) |
| ORM | SQLAlchemy (Async) |
| Authentication | JWT (JSON Web Tokens) |
| Password Hashing | bcrypt |
| File Storage | Local Filesystem (development) |
| API Docs | Swagger UI (auto-generated) / Postman |

### Database
| Layer | Technology |
|---|---|
| Engine | PostgreSQL 15+ |
| Migrations | Alembic |
| Connection | SQLAlchemy AsyncSession |

### Architecture
- **REST API** with proper HTTP verbs and status codes
- **Clean Architecture** — Routers → Services → Repositories → Models
- **Modular Folder Structure**

---

## UI Design System

The interface is designed as a **premium enterprise SaaS product**, inspired by:

> SAP Fiori · Microsoft Dynamics · Oracle ERP · Odoo · Linear · Notion

### Color Palette

| Token | Value | Usage |
|---|---|---|
| `--color-primary` | `#1E3A8A` | Brand, buttons, highlights |
| `--color-secondary` | `#2563EB` | Interactive elements, links |
| `--color-background` | `#F8FAFC` | Page background |
| `--color-sidebar` | `#111827` | Navigation sidebar |
| `--color-card` | `#FFFFFF` | Card surfaces |
| `--color-border` | `#E2E8F0` | Borders, dividers |
| `--color-text-primary` | `#0F172A` | Headings |
| `--color-text-secondary` | `#64748B` | Body, labels |
| `--color-success` | `#10B981` | Success states |
| `--color-warning` | `#F59E0B` | Warning states |
| `--color-danger` | `#EF4444` | Error states |
| `--color-info` | `#3B82F6` | Info states |

### Design Tokens

```css
--border-radius-sm: 6px;
--border-radius-md: 12px;
--border-radius-lg: 16px;
--border-radius-xl: 24px;
--shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
--shadow-md: 0 4px 16px rgba(0,0,0,0.10);
--shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
--transition-fast: 150ms ease;
--transition-normal: 300ms ease;
--font-family: ''Inter'', system-ui, sans-serif;
```

### Responsiveness
- **Desktop First** — Full sidebar layout
- **Tablet Compatible** — Collapsible sidebar
- **Mobile Compatible** — Drawer navigation

### Required UI Components (Every Table/List View)

| Component | Required |
|---|---|
| Search bar | YES |
| Column sorting | YES |
| Pagination | YES |
| Multi-filter panel | YES |
| Status badges (colored) | YES |
| Row-level action icons | YES |
| Confirmation dialogs | YES |
| Toast notifications | YES |
| Loading skeletons | YES |
| Empty state illustrations | YES |
| Error pages (404, 403, 500) | YES |

---

## Project Structure

```
assetflow/
|
+-- backend/
|   +-- main.py                          # FastAPI app entry point
|   +-- config.py                        # Settings (env vars, DB URL, JWT secrets)
|   +-- database.py                      # Async SQLAlchemy engine & session
|   |
|   +-- models/                          # SQLAlchemy ORM models
|   |   +-- __init__.py
|   |   +-- user.py
|   |   +-- department.py
|   |   +-- asset_category.py
|   |   +-- asset.py
|   |   +-- asset_document.py
|   |   +-- asset_image.py
|   |   +-- allocation.py
|   |   +-- transfer.py
|   |   +-- booking.py
|   |   +-- maintenance.py
|   |   +-- audit.py
|   |   +-- notification.py
|   |   +-- activity_log.py
|   |
|   +-- schemas/                         # Pydantic request/response schemas
|   |   +-- auth.py
|   |   +-- user.py
|   |   +-- department.py
|   |   +-- asset_category.py
|   |   +-- asset.py
|   |   +-- allocation.py
|   |   +-- transfer.py
|   |   +-- booking.py
|   |   +-- maintenance.py
|   |   +-- audit.py
|   |   +-- notification.py
|   |   +-- activity_log.py
|   |   +-- report.py
|   |
|   +-- routers/                         # FastAPI route handlers
|   |   +-- auth.py
|   |   +-- users.py
|   |   +-- departments.py
|   |   +-- asset_categories.py
|   |   +-- assets.py
|   |   +-- allocations.py
|   |   +-- transfers.py
|   |   +-- bookings.py
|   |   +-- maintenance.py
|   |   +-- audits.py
|   |   +-- reports.py
|   |   +-- notifications.py
|   |   +-- activity_logs.py
|   |   +-- dashboard.py
|   |
|   +-- services/                        # Business logic layer
|   |   +-- auth_service.py
|   |   +-- user_service.py
|   |   +-- department_service.py
|   |   +-- asset_service.py
|   |   +-- allocation_service.py
|   |   +-- transfer_service.py
|   |   +-- booking_service.py
|   |   +-- maintenance_service.py
|   |   +-- audit_service.py
|   |   +-- report_service.py
|   |   +-- notification_service.py
|   |   +-- dashboard_service.py
|   |
|   +-- repositories/                    # Data access layer (DB queries)
|   |   +-- base_repository.py
|   |   +-- user_repository.py
|   |   +-- department_repository.py
|   |   +-- asset_repository.py
|   |   +-- allocation_repository.py
|   |   +-- transfer_repository.py
|   |   +-- booking_repository.py
|   |   +-- maintenance_repository.py
|   |   +-- audit_repository.py
|   |   +-- notification_repository.py
|   |
|   +-- auth/                            # Authentication utilities
|   |   +-- jwt_handler.py
|   |   +-- password_handler.py
|   |   +-- dependencies.py
|   |   +-- rbac.py
|   |
|   +-- utils/                           # Shared utilities
|   |   +-- exceptions.py
|   |   +-- pagination.py
|   |   +-- qr_generator.py
|   |   +-- tag_generator.py
|   |   +-- file_handler.py
|   |   +-- email_sender.py
|   |   +-- logger.py
|   |   +-- validators.py
|   |   +-- constants.py
|   |
|   +-- migrations/                      # Alembic database migrations
|   |   +-- env.py
|   |   +-- versions/
|   |
|   +-- uploads/                         # Local file storage (dev only)
|   |   +-- assets/images/
|   |   +-- assets/documents/
|   |   +-- qrcodes/
|   |
|   +-- tests/
|   |   +-- conftest.py
|   |   +-- test_auth.py
|   |   +-- test_assets.py
|   |   +-- test_allocations.py
|   |   +-- test_bookings.py
|   |   +-- test_maintenance.py
|   |   +-- test_audits.py
|   |
|   +-- requirements.txt
|   +-- alembic.ini
|   +-- .env.example
|
+-- frontend/
|   +-- index.html                       # Entry point / Login
|   +-- assets/
|   |   +-- css/
|   |   |   +-- main.css
|   |   |   +-- components.css
|   |   |   +-- layout.css
|   |   |   +-- tables.css
|   |   |   +-- forms.css
|   |   |   +-- badges.css
|   |   |   +-- modals.css
|   |   |   +-- toast.css
|   |   |   +-- animations.css
|   |   |
|   |   +-- js/
|   |       +-- core/
|   |       |   +-- api.js
|   |       |   +-- auth.js
|   |       |   +-- router.js
|   |       |   +-- store.js
|   |       |   +-- toast.js
|   |       |   +-- modal.js
|   |       |   +-- utils.js
|   |       |
|   |       +-- components/
|   |       |   +-- sidebar.js
|   |       |   +-- header.js
|   |       |   +-- table.js
|   |       |   +-- pagination.js
|   |       |   +-- filters.js
|   |       |   +-- skeleton.js
|   |       |   +-- empty-state.js
|   |       |   +-- confirmation.js
|   |       |   +-- charts.js
|   |       |
|   |       +-- pages/
|   |           +-- auth/
|   |           |   +-- login.js
|   |           |   +-- register.js
|   |           |   +-- forgot-password.js
|   |           +-- dashboard.js
|   |           +-- departments.js
|   |           +-- categories.js
|   |           +-- employees.js
|   |           +-- assets.js
|   |           +-- asset-detail.js
|   |           +-- allocations.js
|   |           +-- transfers.js
|   |           +-- bookings.js
|   |           +-- maintenance.js
|   |           +-- audits.js
|   |           +-- reports.js
|   |           +-- notifications.js
|   |           +-- activity-logs.js
|   |
|   +-- pages/
|       +-- dashboard.html
|       +-- departments.html
|       +-- categories.html
|       +-- employees.html
|       +-- assets.html
|       +-- asset-detail.html
|       +-- allocations.html
|       +-- transfers.html
|       +-- bookings.html
|       +-- maintenance.html
|       +-- audits.html
|       +-- reports.html
|       +-- notifications.html
|       +-- activity-logs.html
|       +-- 404.html
|       +-- 403.html
|       +-- 500.html
|
+-- .gitignore
+-- .env.example
+-- README.md
```

---

## Database Design

### Design Rules — Every Table Must Have

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID` | Primary key, auto-generated |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | Auto-set on insert |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | Auto-updated on change |
| `is_deleted` | `BOOLEAN` | Soft delete flag |
| `status` | `ENUM / VARCHAR` | Record status |

All foreign keys must be indexed. All query-heavy columns must be indexed.

### Core Tables

| Table | Purpose |
|---|---|
| `users` | All system users with role and department |
| `departments` | Organizational departments |
| `asset_categories` | Asset type classifications |
| `assets` | Main asset registry |
| `asset_images` | Asset photo uploads (1:N) |
| `asset_documents` | Asset document uploads (1:N) |
| `allocations` | Asset allocation records |
| `transfers` | Asset transfer records |
| `bookings` | Resource booking records |
| `maintenance_requests` | Maintenance workflow records |
| `audit_cycles` | Audit cycle metadata |
| `audit_items` | Per-asset audit verification records |
| `notifications` | In-app notification records |
| `activity_logs` | Immutable action audit trail |

---

## Authentication & RBAC

### Authentication Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register` | POST | Creates Employee account only |
| `/api/auth/login` | POST | Returns JWT access + refresh tokens |
| `/api/auth/refresh` | POST | Refreshes access token |
| `/api/auth/logout` | POST | Invalidates refresh token |
| `/api/auth/forgot-password` | POST | Sends reset link via email |
| `/api/auth/reset-password` | POST | Applies new password |
| `/api/auth/me` | GET | Returns current user profile |

### JWT Token Structure

```json
{
  "sub": "user-uuid",
  "email": "user@company.com",
  "role": "asset_manager",
  "department_id": "dept-uuid",
  "exp": 1720000000,
  "iat": 1719996400
}
```

### Role Hierarchy & Permissions Matrix

| Permission | Admin | Asset Manager | Dept. Head | Employee |
|---|:---:|:---:|:---:|:---:|
| Manage Users | YES | NO | NO | NO |
| Promote User Roles | YES | NO | NO | NO |
| Manage Departments | YES | YES | NO | NO |
| Manage Asset Categories | YES | YES | NO | NO |
| Register Assets | YES | YES | NO | NO |
| Approve Allocations | YES | YES | YES | NO |
| Approve Transfers | YES | YES | YES | NO |
| Create Booking | YES | YES | YES | YES |
| Approve Maintenance | YES | YES | YES | NO |
| Assign Technician | YES | YES | NO | NO |
| Create Audit | YES | YES | NO | NO |
| View Reports | YES | YES | YES | NO |
| Export Reports | YES | YES | NO | NO |
| View Notifications | YES | YES | YES | YES |
| View Activity Logs | YES | YES | NO | NO |

> **IMPORTANT:** POST /api/auth/register ALWAYS creates an Employee role.
> Only an Admin can promote via PATCH /api/users/{id}/role

---

## Modules

### 1. Authentication Module
- Email + password login with JWT
- bcrypt password hashing (cost factor 12+)
- Access token (15 min) + refresh token (7 days)
- Forgot password via email token
- Session invalidation on logout

### 2. Dashboard Module

**KPI Cards:**
- Total Assets | Available | Allocated | Under Maintenance
- Pending Transfers | Bookings Today | Upcoming Returns | Overdue Returns

**Charts:**
- Asset Status Distribution (Donut Chart)
- Asset Allocation by Department (Bar Chart)
- Maintenance Trends (Line Chart — 30 days)
- Booking Utilization (Area Chart — 7 days)

### 3. Organization Setup

#### Departments
| Endpoint | Method | Description |
|---|---|---|
| `/api/departments` | GET | List departments (paginated, searchable) |
| `/api/departments` | POST | Create department |
| `/api/departments/{id}` | GET | Department details |
| `/api/departments/{id}` | PUT | Update department |
| `/api/departments/{id}` | DELETE | Soft delete |

#### Asset Categories
| Endpoint | Method | Description |
|---|---|---|
| `/api/asset-categories` | GET | List categories |
| `/api/asset-categories` | POST | Create category |
| `/api/asset-categories/{id}` | PUT | Update category |
| `/api/asset-categories/{id}` | DELETE | Soft delete |

#### Employee Directory
| Endpoint | Method | Description |
|---|---|---|
| `/api/users` | GET | List employees |
| `/api/users/{id}` | GET | Employee profile |
| `/api/users/{id}` | PUT | Update profile |
| `/api/users/{id}/role` | PATCH | Promote/demote role (Admin only) |
| `/api/users/{id}/deactivate` | PATCH | Deactivate account |

### 4. Asset Management

**Auto-generated on registration:**
- Asset Tag: `AST-YYYY-XXXXXX` format
- QR Code: PNG, downloadable

| Endpoint | Method | Description |
|---|---|---|
| `/api/assets` | GET | List assets |
| `/api/assets` | POST | Register asset |
| `/api/assets/{id}` | GET | Asset detail + history |
| `/api/assets/{id}` | PUT | Update asset |
| `/api/assets/{id}/images` | POST | Upload images |
| `/api/assets/{id}/documents` | POST | Upload documents |
| `/api/assets/{id}/qrcode` | GET | Download QR code |
| `/api/assets/{id}/history` | GET | Full lifecycle history |
| `/api/assets/{id}/status` | PATCH | Manual status override (Admin) |

### 5. Asset Allocation & Transfer

**Allocation Workflow:** Request → Approval → Active → Return

| Endpoint | Method | Description |
|---|---|---|
| `/api/allocations` | GET | List allocations |
| `/api/allocations` | POST | Create allocation request |
| `/api/allocations/{id}/approve` | PATCH | Approve |
| `/api/allocations/{id}/reject` | PATCH | Reject |
| `/api/allocations/{id}/return` | PATCH | Mark returned |
| `/api/transfers` | GET | List transfers |
| `/api/transfers` | POST | Request transfer |
| `/api/transfers/{id}/approve` | PATCH | Approve |
| `/api/transfers/{id}/reject` | PATCH | Reject |
| `/api/transfers/{id}/complete` | PATCH | Complete |

### 6. Resource Booking

**Conflict Detection:** Overlapping bookings for the same asset are rejected.

| Endpoint | Method | Description |
|---|---|---|
| `/api/bookings` | GET | List bookings |
| `/api/bookings` | POST | Create booking |
| `/api/bookings/{id}/cancel` | PATCH | Cancel |
| `/api/bookings/{id}/confirm` | PATCH | Confirm |
| `/api/bookings/availability` | GET | Check availability |

### 7. Maintenance

**Workflow:** Raised → Approved → Assigned → In Progress → Resolved

| Endpoint | Method | Description |
|---|---|---|
| `/api/maintenance` | GET | List requests |
| `/api/maintenance` | POST | Raise request |
| `/api/maintenance/{id}/approve` | PATCH | Approve |
| `/api/maintenance/{id}/reject` | PATCH | Reject |
| `/api/maintenance/{id}/assign` | PATCH | Assign technician |
| `/api/maintenance/{id}/start` | PATCH | Start work |
| `/api/maintenance/{id}/resolve` | PATCH | Mark resolved |

### 8. Audit

**Workflow:** Create Cycle → Assign Auditor → Verify Assets → Generate Report

| Endpoint | Method | Description |
|---|---|---|
| `/api/audits` | GET | List audit cycles |
| `/api/audits` | POST | Create cycle |
| `/api/audits/{id}/assign` | PATCH | Assign auditor |
| `/api/audits/{id}/start` | PATCH | Start audit |
| `/api/audits/{id}/items/{item_id}/verify` | PATCH | Verify asset |
| `/api/audits/{id}/items/{item_id}/flag` | PATCH | Flag missing/damaged |
| `/api/audits/{id}/close` | PATCH | Close cycle |
| `/api/audits/{id}/report` | GET | Discrepancy report |

### 9. Reports & Analytics

| Report | Formats |
|---|---|
| Asset Summary (by category, dept, status) | CSV, PDF |
| Allocation Report (active, returned, overdue) | CSV, PDF |
| Booking Report (by asset, user, date range) | CSV, PDF |
| Maintenance Report (by status, resolution time) | CSV, PDF |
| Audit Discrepancy Report | CSV, PDF |
| Idle Assets Report | CSV, PDF |
| Department Utilization Report | CSV, PDF |

### 10. Notifications

| Event | Trigger |
|---|---|
| ASSET_ASSIGNED | Allocation approved |
| ALLOCATION_REJECTED | Allocation rejected |
| BOOKING_CONFIRMED | Booking confirmed |
| BOOKING_CANCELLED | Booking cancelled |
| BOOKING_REMINDER | 24h before booking |
| MAINTENANCE_APPROVED | Maintenance approved |
| MAINTENANCE_REJECTED | Maintenance rejected |
| MAINTENANCE_RESOLVED | Maintenance resolved |
| TRANSFER_APPROVED | Transfer approved |
| TRANSFER_REJECTED | Transfer rejected |
| AUDIT_CREATED | New audit cycle |
| AUDIT_CLOSED | Audit closed |
| OVERDUE_RETURN | Return date passed |
| ROLE_CHANGED | User role updated |

---

## Asset Lifecycle

```
                      +-------------+
                      |  AVAILABLE  |<-----------------------+
                      +------+------+                        |
                             |                               |
             +---------------+---------------+               |
             v               v               v               |
      +------------+  +-----------+  +----------------+      |
      | ALLOCATED  |  | RESERVED  |  | UNDER MAINT.   |      |
      +------+-----+  +-----+-----+  +-------+--------+      |
             |              |                |               |
             |    +---------+                +---------------+
             |    |
             v    v
      +------------+
      |    LOST    |
      +------+-----+
             |
      +------+-----+
      v            v
+----------+  +----------+
| RETIRED  |  | DISPOSED |
+----------+  +----------+
```

### Valid State Transitions

| From | To | Trigger |
|---|---|---|
| Available | Allocated | Allocation approved |
| Available | Reserved | Booking confirmed |
| Available | Under Maintenance | Maintenance approved |
| Allocated | Available | Asset returned |
| Allocated | Under Maintenance | Maintenance raised |
| Reserved | Available | Booking cancelled/completed |
| Under Maintenance | Available | Maintenance resolved |
| Any | Lost | Admin marks as lost |
| Lost / Available | Retired | Admin retires asset |
| Retired | Disposed | Admin disposes asset |

> Invalid transitions return HTTP 422 with a meaningful error message.

---

## Business Rules

1. **No Double Allocation** — Conflict detection before every allocation approval
2. **No Booking Overlaps** — Overlap check before every booking creation
3. **Automatic Status Updates** — Asset status is always atomically updated with workflow changes
4. **Complete History** — Every state change logged with user, timestamp, and reason
5. **Notification Automation** — Every significant event auto-creates notification records
6. **Activity Logging** — Every API write operation generates an activity log entry
7. **Soft Deletes** — No record is permanently deleted; `is_deleted` flag is used
8. **Role Enforcement** — Every endpoint validates the authenticated user's role
9. **Overdue Detection** — Background task checks daily for overdue returns
10. **Audit Trail** — Every allocation, transfer, booking, maintenance, and audit action is fully traceable

---

## API Design

### Base URL
```
/api/v1/
```

### Query Parameters (All List Endpoints)

```
?search=keyword          Full-text search
&status=active           Exact status filter
&category_id=uuid        Relation filter
&department_id=uuid      Relation filter
&sort_by=created_at      Sort column
&sort_order=desc         asc | desc
&page=1                  Page number (1-indexed)
&per_page=20             Items per page (max 100)
&date_from=2024-01-01   Date range start
&date_to=2024-12-31     Date range end
```

### Standard Response Envelope

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {},
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  }
}
```

### Error Response

```json
{
  "success": false,
  "message": "Asset is already allocated",
  "error_code": "ASSET_ALREADY_ALLOCATED",
  "details": {}
}
```

### HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | OK |
| 201 | Created |
| 204 | No Content (delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized |
| 403 | Forbidden (insufficient role) |
| 404 | Not Found |
| 409 | Conflict (duplicate/overlap) |
| 422 | Unprocessable Entity (invalid state transition) |
| 429 | Too Many Requests (rate limit) |
| 500 | Internal Server Error |

---

## Security

| Control | Implementation |
|---|---|
| Authentication | JWT Bearer tokens (access + refresh) |
| Password Hashing | bcrypt with cost factor >= 12 |
| Authorization | Role-based middleware on every endpoint |
| Input Validation | Pydantic schemas on all request bodies |
| SQL Injection | SQLAlchemy ORM (parameterized queries only) |
| XSS Protection | Output encoding in frontend |
| Rate Limiting | FastAPI SlowAPI middleware |
| CORS | Configured whitelist (localhost only in dev) |
| Token Expiry | Access: 15 min, Refresh: 7 days |
| File Validation | MIME type and size validation on upload |

---

## Search, Filters & Pagination

Every list endpoint supports:
- Full-text search across relevant columns
- Multiple simultaneous filters
- Column sorting (asc/desc)
- Cursor-based or offset pagination
- Date range filters

---

## Notifications

### Delivery Methods
1. **In-App** — Stored in `notifications` table, polled every 30 seconds
2. **Email** — Sent via SMTP for critical events (configurable)

### Notification Bell Behavior
- Shows unread count badge
- Dropdown shows latest 10 notifications
- "Mark all as read" button
- Click navigates to relevant record

---

## Logging & Audit Trail

### Activity Log Entry

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "user_name": "John Doe",
  "action": "ASSET_ALLOCATED",
  "module": "allocations",
  "record_id": "uuid",
  "description": "Asset Dell Laptop AST-2024-000123 allocated to Jane Smith",
  "ip_address": "192.168.1.10",
  "created_at": "2024-07-12T11:00:00Z"
}
```

### Logged Actions Per Module

| Module | Actions Logged |
|---|---|
| Auth | login, logout, register, password_reset |
| Assets | created, updated, deleted, status_changed |
| Allocations | requested, approved, rejected, returned |
| Transfers | requested, approved, rejected, completed |
| Bookings | created, confirmed, cancelled, completed |
| Maintenance | raised, approved, rejected, assigned, started, resolved |
| Audits | created, started, closed, item_verified, item_flagged |
| Users | created, updated, role_changed, deactivated |

---

## Development Phases

### Phase 1 — Foundation
- [ ] Project initialization and folder structure
- [ ] PostgreSQL connection with SQLAlchemy async
- [ ] Alembic migrations setup
- [ ] JWT authentication (register, login, refresh, logout)
- [ ] Forgot/reset password flow
- [ ] Base models (UUID, timestamps, soft delete)
- [ ] Global error handlers and response envelopes
- [ ] Logging middleware
- [ ] CORS and security headers

### Phase 2 — Organization Setup
- [ ] Department CRUD with search/filter/pagination
- [ ] Asset Category CRUD
- [ ] Employee directory management
- [ ] Role promotion by Admin
- [ ] Frontend: Login, Register pages
- [ ] Frontend: Department, Category, Employee pages

### Phase 3 — Asset Management
- [ ] Asset registration with image/document upload
- [ ] Asset tag auto-generation (AST-YYYY-XXXXXX)
- [ ] QR code generation and download
- [ ] Asset lifecycle state machine
- [ ] Asset detail view with full history
- [ ] Frontend: Asset list and detail pages

### Phase 4 — Allocation & Transfer
- [ ] Allocation request → approval → return workflow
- [ ] Transfer request → approval → completion
- [ ] Conflict detection engine
- [ ] Expected return date tracking
- [ ] Overdue detection (background task)
- [ ] Frontend: Allocation and transfer pages

### Phase 5 — Resource Booking
- [ ] Booking creation with overlap detection
- [ ] Calendar view integration
- [ ] Booking confirmation and cancellation
- [ ] 24h booking reminders (background task)
- [ ] Frontend: Booking list and calendar pages

### Phase 6 — Maintenance
- [ ] Maintenance request workflow
- [ ] Technician assignment
- [ ] Status progression tracking
- [ ] Frontend: Maintenance pages

### Phase 7 — Audit
- [ ] Audit cycle creation and assignment
- [ ] Asset verification workflow
- [ ] Missing/damaged asset flagging
- [ ] Discrepancy report generation
- [ ] Frontend: Audit pages

### Phase 8 — Reports, Notifications & Dashboard
- [ ] Dashboard KPI aggregation APIs
- [ ] Dashboard charts (Chart.js)
- [ ] All report generation APIs
- [ ] CSV export
- [ ] PDF export (ReportLab / WeasyPrint)
- [ ] Notification system (in-app + email)
- [ ] Activity log viewer
- [ ] Frontend: Dashboard, Reports, Notifications pages

### Phase 9 — Testing & Optimization
- [ ] Unit tests for all services
- [ ] Integration tests for all API endpoints
- [ ] Database query optimization
- [ ] Index optimization
- [ ] API response time profiling
- [ ] Security testing
- [ ] Cross-browser UI testing
- [ ] Bug fixes and code review

---

## Coding Standards

### Backend (Python / FastAPI)
- Follow PEP 8 style guide
- Use type hints everywhere
- Use async/await for all I/O operations
- Use Pydantic v2 for all schemas
- Use dependency injection for DB sessions and auth
- Use custom exceptions — never raise generic Exception
- Use meaningful variable names
- Every function must have a docstring
- Organize imports: stdlib → third-party → local

### Frontend (JavaScript)
- Use ES6+ modules (import/export)
- Use async/await — no raw .then() chains
- Use centralized API client — never write fetch() directly in page scripts
- Use component pattern — every UI section is a reusable function
- Write JSDoc comments for all functions
- Validate all inputs on frontend before API call
- Handle all API errors gracefully with toast notifications

### Database
- Use migrations for all schema changes
- Use indexes on all foreign keys and search columns
- Use transactions for multi-table writes
- Never use SELECT * in production queries
- Use connection pooling (SQLAlchemy pool config)

---

## Team Roles

| Role | Responsibility |
|---|---|
| Senior Software Architect | Overall system design, Clean Architecture enforcement |
| Senior Full Stack Developer | Frontend-backend integration, end-to-end delivery |
| Senior FastAPI Developer | API design, backend services, authentication, performance |
| Senior PostgreSQL Architect | Schema design, normalization, indexing, query optimization |
| Senior UI/UX Designer | Design system, component library, user experience |
| Senior Security Engineer | Auth, input validation, security headers, threat modeling |
| Senior QA Engineer | Test strategy, automated tests, regression, bug reporting |

---

## Getting Started (Development Setup)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### 1. Clone Repository

```bash
git clone https://github.com/your-org/assetflow.git
cd assetflow
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate        # Mac/Linux
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with database credentials and JWT secret
```

### 4. Database Setup

```bash
createdb assetflow_db
alembic upgrade head
```

### 5. Run Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 7. Run Frontend

```bash
python -m http.server 3000 --directory frontend
# Open http://localhost:3000 in browser
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/assetflow_db

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=AssetFlow
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp
ALLOWED_DOCUMENT_TYPES=application/pdf

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@assetflow.com

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## Key Dependencies

### Backend (requirements.txt)

```
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
pydantic>=2.7.0
pydantic-settings>=2.3.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
pillow>=10.3.0
qrcode>=7.4.2
reportlab>=4.2.0
slowapi>=0.1.9
python-dotenv>=1.0.0
pytest>=8.2.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
```

---

## License

This project is proprietary and confidential.
All rights reserved (c) 2025 AssetFlow.

---

*Built with care by the AssetFlow Engineering Team*
