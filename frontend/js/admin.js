/** Admin panel logic — analytics + user management */
if (!requireAuth()) throw new Error('Not authenticated');

// ─── Load Analytics ────────────────────────────────
async function loadAnalytics() {
  const res = await api.getAnalytics();
  if (res.ok) {
    document.getElementById('stat-total').textContent = res.data.total_users;
    document.getElementById('stat-faces').textContent = res.data.users_with_faces;
    document.getElementById('stat-status').textContent = res.data.system_status === 'operational'
      ? '✓ Operational' : res.data.system_status;
  }
}

// ─── Load Users ────────────────────────────────────
async function loadUsers() {
  const res = await api.listUsers();
  const tbody = document.getElementById('users-tbody');

  if (!res.ok) {
    if (res.status === 403) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:var(--space-2xl)">
        <span class="badge badge-danger">⛔ Admin access required</span>
        <p class="text-muted mt-md" style="font-size:0.85rem">You need an admin token to view this page.</p>
      </td></tr>`;
    } else if (res.status === 401) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:var(--space-2xl)">
        <span class="badge badge-warning">🔒 Not authenticated</span>
      </td></tr>`;
    } else {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center">Failed to load users</td></tr>`;
    }
    return;
  }

  const users = res.data;
  if (!users || users.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:var(--space-2xl)">No users found</td></tr>`;
    return;
  }

  tbody.innerHTML = users.map(u => {
    const created = u.created_at ? new Date(u.created_at).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric'
    }) : '—';
    const faceBadge = u.has_face_embedding
      ? '<span class="badge badge-success">✓ Registered</span>'
      : '<span class="badge badge-warning">✗ Not Set</span>';

    return `<tr>
      <td style="color:var(--text-primary);font-weight:500">${escapeHtml(u.email)}</td>
      <td>${faceBadge}</td>
      <td>${created}</td>
      <td>
        <button class="btn btn-sm btn-danger" onclick="deleteUser('${u.id}','${escapeHtml(u.email)}')">
          Delete
        </button>
      </td>
    </tr>`;
  }).join('');
}

// ─── Delete User ───────────────────────────────────
async function deleteUser(id, email) {
  if (!confirm(`Delete user "${email}"? This cannot be undone.`)) return;
  const res = await api.deleteUser(id);
  if (res.ok || res.status === 204) {
    showAlert('alert-area', `User "${email}" deleted`, 'success');
    loadUsers();
    loadAnalytics();
  } else {
    showAlert('alert-area', res.data?.detail || 'Delete failed', 'error');
  }
}

// ─── Helpers ───────────────────────────────────────
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ─── Init ──────────────────────────────────────────
loadAnalytics();
loadUsers();
