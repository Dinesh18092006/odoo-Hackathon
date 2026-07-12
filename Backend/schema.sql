-- AssetFlow Database Schema
-- Run this SQL in your MySQL instance before starting the backend.

CREATE DATABASE IF NOT EXISTS assetflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE assetflow;

-- ─────────────────────────────────────────
-- DEPARTMENTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120) NOT NULL UNIQUE,
    parent_id   INT NULL REFERENCES departments(id) ON DELETE SET NULL,
    head_id     INT NULL,           -- FK set after employees table
    status      ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- EMPLOYEES / USERS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS employees (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(160) NOT NULL,
    email           VARCHAR(200) NOT NULL UNIQUE,
    password_hash   VARCHAR(256) NOT NULL,
    role            ENUM('Admin','AssetManager','DepartmentHead','Employee') NOT NULL DEFAULT 'Employee',
    department_id   INT NULL REFERENCES departments(id) ON DELETE SET NULL,
    status          ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    reset_token     VARCHAR(128) NULL,
    reset_token_exp DATETIME NULL
);

ALTER TABLE departments
    ADD CONSTRAINT fk_dept_head FOREIGN KEY (head_id) REFERENCES employees(id) ON DELETE SET NULL;

-- ─────────────────────────────────────────
-- ASSET CATEGORIES
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS asset_categories (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(120) NOT NULL UNIQUE,
    extra_fields    JSON NULL,    -- e.g. {"warranty_months": true}
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- ASSETS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS assets (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    asset_tag       VARCHAR(20)  NOT NULL UNIQUE,   -- AF-0001
    name            VARCHAR(200) NOT NULL,
    category_id     INT NOT NULL REFERENCES asset_categories(id),
    serial_number   VARCHAR(120) NULL,
    acquisition_date DATE NULL,
    acquisition_cost DECIMAL(12,2) NULL,
    `condition`     ENUM('New','Good','Fair','Poor') NOT NULL DEFAULT 'New',
    location        VARCHAR(200) NULL,
    status          ENUM('Available','Allocated','Reserved','UnderMaintenance','Lost','Retired','Disposed') NOT NULL DEFAULT 'Available',
    is_bookable     TINYINT(1) NOT NULL DEFAULT 0,
    photo_url       VARCHAR(500) NULL,
    documents_url   VARCHAR(500) NULL,
    extra_data      JSON NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- auto-increment sequence for tag
CREATE TABLE IF NOT EXISTS asset_tag_seq (
    id INT AUTO_INCREMENT PRIMARY KEY
);

-- ─────────────────────────────────────────
-- ALLOCATIONS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS allocations (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    asset_id            INT NOT NULL REFERENCES assets(id),
    employee_id         INT NULL REFERENCES employees(id),
    department_id       INT NULL REFERENCES departments(id),
    allocated_by        INT NOT NULL REFERENCES employees(id),
    allocated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    expected_return_date DATE NULL,
    returned_at         DATETIME NULL,
    condition_checkin   TEXT NULL,
    status              ENUM('Active','Returned','Overdue') NOT NULL DEFAULT 'Active'
);

-- ─────────────────────────────────────────
-- TRANSFER REQUESTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transfer_requests (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    asset_id        INT NOT NULL REFERENCES assets(id),
    requested_by    INT NOT NULL REFERENCES employees(id),
    from_employee   INT NULL REFERENCES employees(id),
    to_employee     INT NULL REFERENCES employees(id),
    reason          TEXT NULL,
    status          ENUM('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending',
    reviewed_by     INT NULL REFERENCES employees(id),
    reviewed_at     DATETIME NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- RESOURCE BOOKINGS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    asset_id        INT NOT NULL REFERENCES assets(id),
    booked_by       INT NOT NULL REFERENCES employees(id),
    start_time      DATETIME NOT NULL,
    end_time        DATETIME NOT NULL,
    purpose         TEXT NULL,
    status          ENUM('Upcoming','Ongoing','Completed','Cancelled') NOT NULL DEFAULT 'Upcoming',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- MAINTENANCE REQUESTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS maintenance_requests (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    asset_id        INT NOT NULL REFERENCES assets(id),
    raised_by       INT NOT NULL REFERENCES employees(id),
    description     TEXT NOT NULL,
    priority        ENUM('Low','Medium','High','Critical') NOT NULL DEFAULT 'Medium',
    photo_url       VARCHAR(500) NULL,
    status          ENUM('Pending','Approved','Rejected','AssignedTechnician','InProgress','Resolved') NOT NULL DEFAULT 'Pending',
    technician_id   INT NULL REFERENCES employees(id),
    reviewed_by     INT NULL REFERENCES employees(id),
    reviewed_at     DATETIME NULL,
    resolved_at     DATETIME NULL,
    notes           TEXT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- AUDIT CYCLES
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_cycles (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    scope_dept_id   INT NULL REFERENCES departments(id),
    scope_location  VARCHAR(200) NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    status          ENUM('Open','Closed') NOT NULL DEFAULT 'Open',
    created_by      INT NOT NULL REFERENCES employees(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_auditors (
    audit_id    INT NOT NULL REFERENCES audit_cycles(id) ON DELETE CASCADE,
    employee_id INT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    PRIMARY KEY (audit_id, employee_id)
);

CREATE TABLE IF NOT EXISTS audit_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    audit_id    INT NOT NULL REFERENCES audit_cycles(id) ON DELETE CASCADE,
    asset_id    INT NOT NULL REFERENCES assets(id),
    auditor_id  INT NOT NULL REFERENCES employees(id),
    result      ENUM('Pending','Verified','Missing','Damaged') NOT NULL DEFAULT 'Pending',
    notes       TEXT NULL,
    checked_at  DATETIME NULL
);

-- ─────────────────────────────────────────
-- NOTIFICATIONS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    body        TEXT NOT NULL,
    type        VARCHAR(60) NOT NULL,   -- 'allocation','maintenance','booking', etc.
    is_read     TINYINT(1) NOT NULL DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- ACTIVITY LOG
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activity_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    actor_id    INT NULL REFERENCES employees(id) ON DELETE SET NULL,
    action      VARCHAR(120) NOT NULL,
    entity_type VARCHAR(60)  NOT NULL,
    entity_id   INT NULL,
    details     JSON NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- SEED: Default Admin
-- password: Admin@123  (bcrypt hash)
-- ─────────────────────────────────────────
INSERT IGNORE INTO employees (name, email, password_hash, role)
VALUES ('System Admin', 'admin@assetflow.local',
        '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Admin');