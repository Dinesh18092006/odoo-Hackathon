/* ═══════════════════════════════════════════════════════════════
   AssetFlow — Injects the sidebar HTML into #sidebar-mount
   Call: injectSidebar() then initSidebar()
   ═══════════════════════════════════════════════════════════════ */

function injectSidebar() {
  const mount = document.getElementById('sidebar-mount');
  if (!mount) return;
  const user = Auth.getUser();
  const role = user?.role || 'Employee';

  const adminItems = role === 'Admin' ? `
    <div class="nav-section-label">Administration</div>
    <a class="nav-link" data-page="organization.html" href="organization.html">
      <span class="nav-icon">🏢</span> Organization Setup
    </a>
  ` : '';

  const mgmtItems = ['Admin','AssetManager'].includes(role) ? `
    <a class="nav-link" data-page="audits.html" href="audits.html">
      <span class="nav-icon">🔍</span> Audit Cycles
    </a>
  ` : '';

  mount.innerHTML = `
    <aside class="sidebar">
      <div class="sidebar-logo">
        <a class="logo-mark" href="dashboard.html">
          <div class="logo-icon">📦</div>
          <span class="logo-text">Asset<span>Flow</span></span>
        </a>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-label">Overview</div>
        <a class="nav-link" data-page="dashboard.html" href="dashboard.html">
          <span class="nav-icon">📊</span> Dashboard
        </a>
        <a class="nav-link" data-page="notifications.html" href="notifications.html">
          <span class="nav-icon">🔔</span> Notifications
          <span class="nav-badge" id="notif-badge" style="display:none">0</span>
        </a>

        <div class="nav-section-label">Assets</div>
        <a class="nav-link" data-page="assets.html" href="assets.html">
          <span class="nav-icon">🏷️</span> Asset Directory
        </a>
        <a class="nav-link" data-page="allocations.html" href="allocations.html">
          <span class="nav-icon">🔄</span> Allocations
        </a>
        <a class="nav-link" data-page="bookings.html" href="bookings.html">
          <span class="nav-icon">📅</span> Resource Booking
        </a>
        <a class="nav-link" data-page="maintenance.html" href="maintenance.html">
          <span class="nav-icon">🔧</span> Maintenance
        </a>

        ${adminItems}
        ${mgmtItems}

        <div class="nav-section-label">Insights</div>
        <a class="nav-link" data-page="reports.html" href="reports.html">
          <span class="nav-icon">📈</span> Reports
        </a>
        <a class="nav-link" data-page="logs.html" href="logs.html">
          <span class="nav-icon">📋</span> Activity Logs
        </a>
      </nav>

      <div class="sidebar-footer">
        <div class="user-pill">
          <div class="user-avatar" id="sidebar-user-avatar">A</div>
          <div class="user-info">
            <div class="user-name" id="sidebar-user-name">Loading…</div>
            <div class="user-role" id="sidebar-user-role"></div>
          </div>
          <button class="btn-logout" id="btn-logout" title="Sign out">⏏</button>
        </div>
      </div>
    </aside>
  `;
}