/**
 * Centralized API client for AssetFlow.
 * All API calls go through this module — never use fetch() directly in page scripts.
 */

const API_BASE = 'http://localhost:8000/api/v1';

/**
 * Core fetch wrapper with automatic token injection and error handling.
 * @param {string} endpoint - API path (e.g. '/assets')
 * @param {object} options - fetch options
 * @returns {Promise<object>} - Parsed response body
 */
async function request(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const headers = {
    ...options.headers,
  };
  
  // Only set Content-Type for non-FormData requests
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 — try to refresh token
  if (response.status === 401) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      // Retry original request with new token
      headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
      const retryResponse = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
      return parseResponse(retryResponse);
    } else {
      // Refresh failed — redirect to login
      window.location.href = '/index.html';
      return;
    }
  }

  return parseResponse(response);
}

async function parseResponse(response) {
  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { message: text };
  }

  if (!response.ok) {
    const error = new Error(data.message || `HTTP ${response.status}`);
    error.status = response.status;
    error.errorCode = data.error_code || 'ERROR';
    error.data = data;
    throw error;
  }

  // Normalize pagination data structure for the frontend
  if (data.pagination && Array.isArray(data.data)) {
    data.data = {
      items: data.data,
      total: data.pagination.total,
      page: data.pagination.page,
      pages: data.pagination.pages,
      per_page: data.pagination.per_page
    };
  }

  return data;
}

async function tryRefreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!response.ok) return false;
    const data = await response.json();
    localStorage.setItem('access_token', data.data.access_token);
    return true;
  } catch {
    return false;
  }
}

// HTTP method helpers
export const api = {
  get: (endpoint, params = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== '' && v != null)
    ).toString();
    return request(`${endpoint}${query ? `?${query}` : ''}`);
  },
  post: (endpoint, body) => request(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  postForm: (endpoint, formData) => request(endpoint, { method: 'POST', body: formData }),
  put: (endpoint, body) => request(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  patch: (endpoint, body = {}) => request(endpoint, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (endpoint) => request(endpoint, { method: 'DELETE' }),
};

// ==================== API MODULES ====================

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  refresh: (token) => api.post('/auth/refresh', { refresh_token: token }),
  me: () => api.get('/auth/me'),
  changePassword: (data) => api.post('/auth/change-password', data),
};

export const usersApi = {
  list: (params) => api.get('/users', params),
  get: (id) => api.get(`/users/${id}`),
  update: (id, data) => api.put(`/users/${id}`, data),
  updateRole: (id, role) => api.patch(`/users/${id}/role`, { role }),
  deactivate: (id) => api.patch(`/users/${id}/deactivate`),
};

export const departmentsApi = {
  list: (params) => api.get('/departments', params),
  get: (id) => api.get(`/departments/${id}`),
  create: (data) => api.post('/departments', data),
  update: (id, data) => api.put(`/departments/${id}`, data),
  delete: (id) => api.delete(`/departments/${id}`),
};

export const categoriesApi = {
  list: (params) => api.get('/asset-categories', params),
  get: (id) => api.get(`/asset-categories/${id}`),
  create: (data) => api.post('/asset-categories', data),
  update: (id, data) => api.put(`/asset-categories/${id}`, data),
  delete: (id) => api.delete(`/asset-categories/${id}`),
};

export const assetsApi = {
  list: (params) => api.get('/assets', params),
  get: (id) => api.get(`/assets/${id}`),
  create: (data) => api.post('/assets', data),
  update: (id, data) => api.put(`/assets/${id}`, data),
  delete: (id) => api.delete(`/assets/${id}`),
  changeStatus: (id, data) => api.patch(`/assets/${id}/status`, data),
  uploadImage: (id, formData) => api.postForm(`/assets/${id}/images`, formData),
  deleteImage: (id, imgId) => api.delete(`/assets/${id}/images/${imgId}`),
  uploadDocument: (id, formData) => api.postForm(`/assets/${id}/documents`, formData),
  deleteDocument: (id, docId) => api.delete(`/assets/${id}/documents/${docId}`),
  downloadQR: (id) => `${API_BASE}/assets/${id}/qrcode`,
};

export const allocationsApi = {
  list: (params) => api.get('/allocations', params),
  get: (id) => api.get(`/allocations/${id}`),
  create: (data) => api.post('/allocations', data),
  approve: (id) => api.patch(`/allocations/${id}/approve`),
  reject: (id, reason) => api.patch(`/allocations/${id}/reject`, { rejection_reason: reason }),
  return: (id) => api.patch(`/allocations/${id}/return`),
};

export const transfersApi = {
  list: (params) => api.get('/transfers', params),
  create: (data) => api.post('/transfers', data),
  approve: (id) => api.patch(`/transfers/${id}/approve`),
  reject: (id, reason) => api.patch(`/transfers/${id}/reject`, { rejection_reason: reason }),
  complete: (id) => api.patch(`/transfers/${id}/complete`),
};

export const bookingsApi = {
  list: (params) => api.get('/bookings', params),
  get: (id) => api.get(`/bookings/${id}`),
  create: (data) => api.post('/bookings', data),
  confirm: (id) => api.patch(`/bookings/${id}/confirm`),
  cancel: (id, reason) => api.patch(`/bookings/${id}/cancel`, { cancellation_reason: reason }),
  checkAvailability: (params) => api.get('/bookings/availability', params),
};

export const maintenanceApi = {
  list: (params) => api.get('/maintenance', params),
  get: (id) => api.get(`/maintenance/${id}`),
  create: (data) => api.post('/maintenance', data),
  approve: (id) => api.patch(`/maintenance/${id}/approve`),
  reject: (id, reason) => api.patch(`/maintenance/${id}/reject`, { rejection_reason: reason }),
  assign: (id, data) => api.patch(`/maintenance/${id}/assign`, data),
  start: (id) => api.patch(`/maintenance/${id}/start`),
  resolve: (id, data) => api.patch(`/maintenance/${id}/resolve`, data),
};

export const auditsApi = {
  list: (params) => api.get('/audits', params),
  get: (id) => api.get(`/audits/${id}`),
  create: (data) => api.post('/audits', data),
  assign: (id, auditorId) => api.patch(`/audits/${id}/assign`, { auditor_id: auditorId }),
  start: (id) => api.patch(`/audits/${id}/start`),
  verify: (id, itemId, data) => api.patch(`/audits/${id}/items/${itemId}/verify`, data),
  flag: (id, itemId, data) => api.patch(`/audits/${id}/items/${itemId}/flag`, data),
  close: (id) => api.patch(`/audits/${id}/close`),
};

export const notificationsApi = {
  list: (params) => api.get('/notifications', params),
  unreadCount: () => api.get('/notifications/unread-count'),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
  markAllRead: () => api.patch('/notifications/read-all'),
};

export const dashboardApi = {
  get: () => api.get('/dashboard'),
};

export const reportsApi = {
  assets: () => api.get('/reports/assets'),
  allocations: (params) => api.get('/reports/allocations', params),
  maintenance: (params) => api.get('/reports/maintenance', params),
};

export const activityLogsApi = {
  list: (params) => api.get('/activity-logs', params),
};
