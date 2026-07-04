/**
 * API Client — Facial Authentication System
 * Handles all HTTP communication with the FastAPI backend.
 */
const API_BASE = 'http://127.0.0.1:8080/api';

const api = {
  /** Get stored auth token */
  getToken() {
    return localStorage.getItem('auth_token');
  },

  /** Get stored refresh token */
  getRefreshToken() {
    return localStorage.getItem('refresh_token');
  },

  /** Save tokens after login/register */
  saveTokens(accessToken, refreshToken) {
    localStorage.setItem('auth_token', accessToken);
    if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
  },

  /** Clear tokens on logout */
  clearTokens() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
  },

  /** Check if user is authenticated */
  isAuthenticated() {
    return !!this.getToken();
  },

  /** Build headers with auth token */
  authHeaders() {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  },

  /** Generic JSON request */
  async request(method, path, body = null, customHeaders = {}) {
    const headers = { ...this.authHeaders(), ...customHeaders };
    const opts = { method, headers };

    if (body && !(body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    } else if (body instanceof FormData) {
      opts.body = body;
    }

    const res = await fetch(`${API_BASE}${path}`, opts);
    const data = res.status === 204 ? null : await res.json().catch(() => null);
    return { ok: res.ok, status: res.status, data };
  },

  // ─── Auth ────────────────────────────────────────────
  async register(email, password) {
    return this.request('POST', '/auth/register', { email, password });
  },

  async registerWithFace(email, password, imageBlob) {
    const form = new FormData();
    form.append('email', email);
    form.append('password', password);
    form.append('file', imageBlob, 'face.jpg');
    return this.request('POST', '/auth/register-with-face', form);
  },

  async login(email, password) {
    return this.request('POST', '/auth/login', { email, password });
  },

  // ─── Face ────────────────────────────────────────────
  async registerFace(imageBlob) {
    const form = new FormData();
    form.append('file', imageBlob, 'face.jpg');
    return this.request('POST', '/face/register', form);
  },

  async loginFace(imageBlob, email = null) {
    const form = new FormData();
    form.append('file', imageBlob, 'face.jpg');
    if (email) form.append('email', email);
    return this.request('POST', '/face/login', form, {});
  },

  // ─── User ───────────────────────────────────────────
  async getProfile() {
    return this.request('GET', '/user/me');
  },

  async updateProfile(data) {
    return this.request('PUT', '/user/me', data);
  },

  async deleteProfile() {
    return this.request('DELETE', '/user/me');
  },

  // ─── Admin ──────────────────────────────────────────
  async listUsers() {
    return this.request('GET', '/admin/users');
  },

  async deleteUser(userId) {
    return this.request('DELETE', `/admin/users/${userId}`);
  },

  // ─── Analytics ──────────────────────────────────────
  async getAnalytics() {
    return this.request('GET', '/analytics/usage');
  },

  // ─── Health ─────────────────────────────────────────
  async healthCheck() {
    try {
      const res = await fetch(`http://127.0.0.1:8080/health`);
      return res.ok;
    } catch {
      return false;
    }
  }
};

/** Redirect to login if not authenticated */
function requireAuth() {
  if (!api.isAuthenticated()) {
    window.location.href = 'index.html';
    return false;
  }
  return true;
}

/** Redirect to dashboard if already authenticated */
function redirectIfAuth() {
  if (api.isAuthenticated()) {
    window.location.href = 'dashboard.html';
  }
}

/** Show alert message in a container */
function showAlert(containerId, message, type = 'error') {
  const container = document.getElementById(containerId);
  if (!container) return;
  const icons = { error: '⚠️', success: '✅', info: 'ℹ️' };
  container.innerHTML = `<div class="alert alert-${type}">${icons[type] || ''} ${message}</div>`;
  setTimeout(() => { container.innerHTML = ''; }, 5000);
}

/** Logout and redirect */
function logout() {
  api.clearTokens();
  window.location.href = 'index.html';
}
