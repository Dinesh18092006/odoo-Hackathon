/**
 * Application state management and auth utilities.
 */

export const App = {
  user: null,
  sidebarCollapsed: false,
  notifCount: 0,

  /** Initialize app — check auth, load user, start polling */
  async init() {
    const token = localStorage.getItem('access_token');
    const publicPages = ['/index.html', '/register.html'];
    const isPublicPage = publicPages.some(p => window.location.pathname.endsWith(p))
      || window.location.pathname === '/';

    if (!token && !isPublicPage) {
      window.location.href = '/index.html';
      return;
    }

    if (token && isPublicPage) {
      window.location.href = '/pages/dashboard.html';
      return;
    }

    if (token) {
      await this.loadCurrentUser();
      this.startNotifPolling();
    }
  },

  async loadCurrentUser() {
    try {
      const { api } = await import('./api.js');
      const res = await import('./api.js');
      const { authApi } = res;
      const result = await authApi.me();
      this.user = result.data;
      this.renderUserInfo();
      this.applyRoleVisibility();
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/index.html';
    }
  },

  renderUserInfo() {
    if (!this.user) return;
    const nameEl = document.getElementById('sidebar-user-name');
    const roleEl = document.getElementById('sidebar-user-role');
    const avatarEl = document.getElementById('sidebar-user-avatar');
    if (nameEl) nameEl.textContent = this.user.full_name;
    if (roleEl) roleEl.textContent = this.user.role.replace(/_/g, ' ');
    if (avatarEl) avatarEl.textContent = this.user.full_name?.charAt(0).toUpperCase() || 'U';
  },

  applyRoleVisibility() {
    if (!this.user) return;
    const role = this.user.role;
    // Hide admin-only elements
    document.querySelectorAll('[data-role]').forEach(el => {
      const allowed = el.dataset.role.split(',').map(r => r.trim());
      if (!allowed.includes(role)) {
        el.style.display = 'none';
      }
    });
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/index.html';
  },

  startNotifPolling() {
    this.pollNotifications();
    setInterval(() => this.pollNotifications(), 30000);
  },

  async pollNotifications() {
    try {
      const { notificationsApi } = await import('./api.js');
      const res = await notificationsApi.unreadCount();
      const count = res.data?.count ?? 0;
      this.notifCount = count;
      const badge = document.getElementById('notif-count');
      if (badge) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = count > 0 ? 'block' : 'none';
      }
      const navBadge = document.getElementById('notif-nav-badge');
      if (navBadge) {
        navBadge.textContent = count;
        navBadge.style.display = count > 0 ? '' : 'none';
      }
    } catch { /* Silently fail — doesn't interrupt UX */ }
  },

  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const header = document.querySelector('.header');
    if (sidebar) sidebar.classList.toggle('collapsed', this.sidebarCollapsed);
    if (mainContent) mainContent.classList.toggle('sidebar-collapsed', this.sidebarCollapsed);
    if (header) header.classList.toggle('sidebar-collapsed', this.sidebarCollapsed);
    localStorage.setItem('sidebar-collapsed', this.sidebarCollapsed);
  },

  initSidebarState() {
    const collapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (collapsed) this.toggleSidebar();
  },

  setActivePage(pageId) {
    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.toggle('active', el.dataset.page === pageId);
    });
  },
};

// Toast notifications
let toastId = 0;
export const Toast = {
  show(title, message = '', type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container') || createToastContainer();
    const id = `toast-${++toastId}`;
    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };

    const toast = document.createElement('div');
    toast.id = id;
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || 'ℹ'}</span>
      <div class="toast-content">
        <div class="toast-title">${escapeHtml(title)}</div>
        ${message ? `<div class="toast-message">${escapeHtml(message)}</div>` : ''}
      </div>
      <button class="toast-close" onclick="document.getElementById('${id}').remove()">×</button>
    `;
    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 300);
    }, duration);

    return id;
  },
  success: (title, msg) => Toast.show(title, msg, 'success'),
  error: (title, msg) => Toast.show(title, msg, 'error'),
  warning: (title, msg) => Toast.show(title, msg, 'warning'),
  info: (title, msg) => Toast.show(title, msg, 'info'),
};

function createToastContainer() {
  const el = document.createElement('div');
  el.id = 'toast-container';
  el.className = 'toast-container';
  document.body.appendChild(el);
  return el;
}

// Modal utility
export const Modal = {
  open(id) {
    const el = document.getElementById(id);
    if (el) {
      el.style.display = 'flex';
      el.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  },
  close(id) {
    const el = document.getElementById(id);
    if (el) {
      el.style.display = 'none';
      el.classList.remove('active');
      document.body.style.overflow = '';
    }
  },
  closeAll() {
    document.querySelectorAll('.modal-overlay').forEach(el => {
      el.style.display = 'none';
      el.classList.remove('active');
    });
    document.body.style.overflow = '';
  },
};

// Format utilities
export const fmt = {
  date(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }); },
  datetime(d) { if (!d) return '—'; return new Date(d).toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); },
  currency(v) { return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(v || 0); },
  fileSize(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  },
  timeAgo(d) {
    if (!d) return '';
    const seconds = Math.floor((new Date() - new Date(d)) / 1000);
    const intervals = [
      [31536000, 'year'], [2592000, 'month'], [86400, 'day'],
      [3600, 'hour'], [60, 'minute'], [1, 'second'],
    ];
    for (const [secs, unit] of intervals) {
      const n = Math.floor(seconds / secs);
      if (n >= 1) return `${n} ${unit}${n > 1 ? 's' : ''} ago`;
    }
    return 'just now';
  },
  status(s) { return s ? s.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : '—'; },
  role(r) { return r ? r.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : '—'; },
};

export function badge(status, label) {
  const text = label || fmt.status(status);
  return `<span class="badge badge-${status.toLowerCase()}">${text}</span>`;
}

export function escapeHtml(str) {
  if (typeof str !== 'string') return str ?? '—';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

// Form utilities
export function getFormData(formId) {
  const form = document.getElementById(formId);
  if (!form) return {};
  const data = {};
  new FormData(form).forEach((value, key) => {
    if (value !== '') data[key] = value;
  });
  return data;
}

export function setFormErrors(errors) {
  document.querySelectorAll('.form-error').forEach(el => el.remove());
  if (!errors) return;
  Object.entries(errors).forEach(([field, msg]) => {
    const input = document.querySelector(`[name="${field}"]`);
    if (input) {
      input.classList.add('is-invalid');
      const err = document.createElement('div');
      err.className = 'form-error';
      err.textContent = msg;
      input.parentNode.appendChild(err);
    }
  });
}

export function clearFormErrors(formId) {
  const form = document.getElementById(formId);
  if (!form) return;
  form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
  form.querySelectorAll('.form-error').forEach(el => el.remove());
}

// Skeleton helpers
export function renderSkeletonRows(count, cols) {
  return Array.from({ length: count }, () => `
    <tr class="skeleton-row-tr">
      ${Array.from({ length: cols }, () => `<td><div class="skeleton skeleton-text"></div></td>`).join('')}
    </tr>
  `).join('');
}

// Debounce
export function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// Confirmation dialog
export async function confirm(title, message, dangerText = 'Confirm') {
  return new Promise((resolve) => {
    const id = 'confirm-modal-' + Date.now();
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = id;
    overlay.style.cssText = 'display:flex;z-index:2000;';
    overlay.innerHTML = `
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3 class="modal-title">${escapeHtml(title)}</h3>
          <button class="modal-close" onclick="document.getElementById('${id}').remove()">×</button>
        </div>
        <div class="modal-body">
          <p style="color:var(--color-text-secondary)">${escapeHtml(message)}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary btn-sm" id="${id}-cancel">Cancel</button>
          <button class="btn btn-danger btn-sm" id="${id}-confirm">${escapeHtml(dangerText)}</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
    document.getElementById(`${id}-cancel`).onclick = () => { overlay.remove(); resolve(false); };
    document.getElementById(`${id}-confirm`).onclick = () => { overlay.remove(); resolve(true); };
  });
}
