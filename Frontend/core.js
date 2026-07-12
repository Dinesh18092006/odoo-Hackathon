/* ═══════════════════════════════════════════════════════════════
   AssetFlow — Core JS
   API client, auth state, toast, modal helpers, page router
   ═══════════════════════════════════════════════════════════════ */

const API = 'http://localhost:8000';

// ── Auth state ─────────────────────────────────────────────────────────────────
const Auth = {
  getToken:   ()   => localStorage.getItem('af_token'),
  getUser:    ()   => { try { return JSON.parse(localStorage.getItem('af_user')); } catch { return null; } },
  setSession: (t,u)=> { localStorage.setItem('af_token', t); localStorage.setItem('af_user', JSON.stringify(u)); },
  clearSession:()  => { localStorage.removeItem('af_token'); localStorage.removeItem('af_user'); },
  isLoggedIn:  ()  => !!localStorage.getItem('af_token'),
  hasRole:     (r) => { const u = Auth.getUser(); return u && (Array.isArray(r) ? r.includes(u.role) : u.role === r); },
};

// ── API Client ─────────────────────────────────────────────────────────────────
async function apiFetch(path, opts = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API + path, { ...opts, headers });

  if (res.status === 401) {
    Auth.clearSession();
    window.location.href = 'index.html';
    return;
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const msg = typeof data?.detail === 'object'
      ? data.detail.detail || JSON.stringify(data.detail)
      : data?.detail || `Error ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

// ── Toast ──────────────────────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  const icons = { success: '✓', error: '✕', warn: '⚠' };
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${icons[type]||'ℹ'}</span><span>${msg}</span>`;
  document.getElementById('toast-container')?.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

// ── Modal helpers ──────────────────────────────────────────────────────────────
function openModal(id) {
  const overlay = document.getElementById(id);
  if (overlay) { overlay.classList.add('open'); }
}
function closeModal(id) {
  const overlay = document.getElementById(id);
  if (overlay) { overlay.classList.remove('open'); }
}
// Close on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// ── Status badge ───────────────────────────────────────────────────────────────
function statusBadge(status) {
  const map = {
    Available:        'green',
    Allocated:        'blue',
    Reserved:         'purple',
    UnderMaintenance: 'orange',
    Lost:             'red',
    Retired:          'gray',
    Disposed:         'gray',
    Active:           'green',
    Inactive:         'gray',
    Pending:          'orange',
    Approved:         'green',
    Rejected:         'red',
    Upcoming:         'blue',
    Ongoing:          'teal',
    Completed:        'green',
    Cancelled:        'gray',
    Resolved:         'green',
    InProgress:       'teal',
    AssignedTechnician:'blue',
    Overdue:          'red',
    Returned:         'green',
    Open:             'blue',
    Closed:           'gray',
    Verified:         'green',
    Missing:          'red',
    Damaged:          'orange',
    Low:              'gray',
    Medium:           'blue',
    High:             'orange',
    Critical:         'red',
  };
  const cls = map[status] || 'gray';
  return `<span class="badge badge-${cls}">${status}</span>`;
}

// ── Role badge ─────────────────────────────────────────────────────────────────
function roleBadge(role) {
  const map = { Admin:'purple', AssetManager:'blue', DepartmentHead:'teal', Employee:'gray' };
  return `<span class="badge badge-${map[role]||'gray'}">${role}</span>`;
}

// ── Date helpers ───────────────────────────────────────────────────────────────
function fmtDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' });
}
function fmtDateTime(d) {
  if (!d) return '—';
  return new Date(d).toLocaleString('en-IN', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' });
}
function isOverdue(dateStr) {
  if (!dateStr) return false;
  return new Date(dateStr) < new Date();
}

// ── Tab switching ──────────────────────────────────────────────────────────────
function initTabs(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      container.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(btn.dataset.tab)?.classList.add('active');
    });
  });
  container.querySelector('.tab-btn')?.click();
}

// ── Guard: redirect to login if not authenticated ──────────────────────────────
function requireAuth(allowedRoles = null) {
  if (!Auth.isLoggedIn()) { window.location.href = 'index.html'; return false; }
  if (allowedRoles && !Auth.hasRole(allowedRoles)) {
    toast('Access denied for your role.', 'error');
    return false;
  }
  return true;
}

// ── Sidebar: set active link & user info ────────────────────────────────────────
function initSidebar() {
  const user = Auth.getUser();
  if (!user) return;

  const nameEl = document.getElementById('sidebar-user-name');
  const roleEl = document.getElementById('sidebar-user-role');
  const avatarEl = document.getElementById('sidebar-user-avatar');
  if (nameEl) nameEl.textContent = user.name;
  if (roleEl) roleEl.textContent = user.role;
  if (avatarEl) avatarEl.textContent = user.name[0].toUpperCase();

  // Mark active nav link
  const page = window.location.pathname.split('/').pop();
  document.querySelectorAll('.nav-link').forEach(a => {
    if (a.dataset.page === page) a.classList.add('active');
  });

  // Role visibility
  document.querySelectorAll('[data-role]').forEach(el => {
    const roles = el.dataset.role.split(',');
    if (!roles.includes(user.role)) el.style.display = 'none';
  });

  // Notification count
  loadNotifCount();

  // Hamburger
  const ham = document.getElementById('hamburger');
  const sidebar = document.querySelector('.sidebar');
  ham?.addEventListener('click', () => sidebar?.classList.toggle('open'));

  // Logout
  document.getElementById('btn-logout')?.addEventListener('click', () => {
    Auth.clearSession();
    window.location.href = 'index.html';
  });
}

async function loadNotifCount() {
  try {
    const data = await apiFetch('/api/dashboard/notifications');
    const unread = data.filter(n => !n.is_read).length;
    const badge = document.getElementById('notif-badge');
    if (badge) badge.textContent = unread > 0 ? unread : '';
    if (badge) badge.style.display = unread > 0 ? 'inline' : 'none';
  } catch {}
}

// ── Dropdown helpers ───────────────────────────────────────────────────────────
async function populateSelect(selectEl, url, valueKey, labelKey, placeholder = 'Select...') {
  selectEl.innerHTML = `<option value="">— ${placeholder} —</option>`;
  try {
    const data = await apiFetch(url);
    data.forEach(item => {
      const opt = document.createElement('option');
      opt.value = item[valueKey];
      opt.textContent = item[labelKey];
      selectEl.appendChild(opt);
    });
  } catch (e) {
    console.warn('populate select error', e);
  }
}

// ── Confirm dialog ─────────────────────────────────────────────────────────────
function confirm(msg) {
  return window.confirm(msg);
}