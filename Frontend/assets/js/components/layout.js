import { App } from '../core/app.js';

export function renderLayout(pageId) {
  const layoutHtml = `
    <!-- Sidebar -->
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-logo">
        <div class="sidebar-logo-icon">AF</div>
        <div class="sidebar-logo-text">
          <h2>AssetFlow</h2>
          <p>Enterprise ERP</p>
        </div>
      </div>
      
      <nav class="sidebar-nav">
        <div class="nav-section-label">Overview</div>
        <a href="dashboard.html" class="nav-item ${pageId === 'dashboard' ? 'active' : ''}" data-page="dashboard">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
          <span class="nav-item-text">Dashboard</span>
        </a>
        
        <div class="nav-section-label" data-role="admin,asset_manager">Organization</div>
        <a href="departments.html" class="nav-item ${pageId === 'departments' ? 'active' : ''}" data-page="departments" data-role="admin,asset_manager">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
          <span class="nav-item-text">Departments</span>
        </a>
        <a href="categories.html" class="nav-item ${pageId === 'categories' ? 'active' : ''}" data-page="categories" data-role="admin,asset_manager">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>
          <span class="nav-item-text">Categories</span>
        </a>
        <a href="employees.html" class="nav-item ${pageId === 'employees' ? 'active' : ''}" data-page="employees" data-role="admin,asset_manager">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
          <span class="nav-item-text">Employees</span>
        </a>

        <div class="nav-section-label">Assets & Resources</div>
        <a href="assets.html" class="nav-item ${pageId === 'assets' ? 'active' : ''}" data-page="assets">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path></svg>
          <span class="nav-item-text">Assets Registry</span>
        </a>
        <a href="allocations.html" class="nav-item ${pageId === 'allocations' ? 'active' : ''}" data-page="allocations">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path></svg>
          <span class="nav-item-text">Allocations</span>
        </a>
        <a href="transfers.html" class="nav-item ${pageId === 'transfers' ? 'active' : ''}" data-page="transfers">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          <span class="nav-item-text">Transfers</span>
        </a>
        <a href="bookings.html" class="nav-item ${pageId === 'bookings' ? 'active' : ''}" data-page="bookings">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
          <span class="nav-item-text">Bookings</span>
        </a>

        <div class="nav-section-label" data-role="admin,asset_manager,department_head">Operations</div>
        <a href="maintenance.html" class="nav-item ${pageId === 'maintenance' ? 'active' : ''}" data-page="maintenance" data-role="admin,asset_manager,department_head">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          <span class="nav-item-text">Maintenance</span>
        </a>
        <a href="audits.html" class="nav-item ${pageId === 'audits' ? 'active' : ''}" data-page="audits" data-role="admin,asset_manager">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
          <span class="nav-item-text">Audits</span>
        </a>
        
        <div class="nav-section-label" data-role="admin,asset_manager,department_head">System</div>
        <a href="reports.html" class="nav-item ${pageId === 'reports' ? 'active' : ''}" data-page="reports" data-role="admin,asset_manager,department_head">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          <span class="nav-item-text">Reports</span>
        </a>
        <a href="activity-logs.html" class="nav-item ${pageId === 'activity-logs' ? 'active' : ''}" data-page="activity-logs" data-role="admin,asset_manager">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span class="nav-item-text">Activity Logs</span>
        </a>
      </nav>

      <div class="sidebar-footer">
        <div class="sidebar-user" id="logout-btn">
          <div class="user-avatar" id="sidebar-user-avatar"></div>
          <div class="sidebar-user-info">
            <div class="sidebar-user-name" id="sidebar-user-name">Loading...</div>
            <div class="sidebar-user-role" id="sidebar-user-role"></div>
          </div>
          <svg style="width:20px;height:20px;color:rgba(255,255,255,0.4)" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
        </div>
      </div>
    </aside>

    <div class="sidebar-overlay" id="sidebar-overlay"></div>

    <!-- Header -->
    <header class="header" id="header">
      <div class="header-left">
        <button class="header-toggle" id="sidebar-toggle">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width:20px;height:20px"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </button>
        <div class="breadcrumb">
          <span class="breadcrumb-item">AssetFlow</span>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current" style="text-transform: capitalize">${pageId.replace('-', ' ')}</span>
        </div>
      </div>
      <div class="header-right">
        <a href="notifications.html" class="notif-btn">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width:20px;height:20px"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
          <span class="notif-count" id="notif-count" style="display:none">0</span>
        </a>
      </div>
    </header>
  `;

  document.body.insertAdjacentHTML('afterbegin', layoutHtml);

  // Bind events
  document.getElementById('sidebar-toggle').addEventListener('click', () => App.toggleSidebar());
  document.getElementById('logout-btn').addEventListener('click', () => App.logout());
  document.getElementById('sidebar-overlay').addEventListener('click', () => App.toggleSidebar());
}
