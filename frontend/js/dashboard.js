/** Dashboard page logic — profile, face registration, edit/delete */
if (!requireAuth()) throw new Error('Not authenticated');

// ─── Load Profile ──────────────────────────────────
async function loadProfile() {
  const res = await api.getProfile();
  if (!res.ok) {
    if (res.status === 401) return logout();
    showAlert('alert-area', 'Failed to load profile', 'error');
    return;
  }

  const user = res.data;
  const initial = (user.email || '?')[0].toUpperCase();
  localStorage.setItem('user_email', user.email);

  document.getElementById('nav-email').textContent = user.email;
  document.getElementById('nav-avatar').textContent = initial;
  document.getElementById('profile-avatar').textContent = initial;
  document.getElementById('profile-email').textContent = user.email;

  const created = user.created_at ? new Date(user.created_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric'
  }) : 'Unknown';
  document.getElementById('profile-meta').textContent = `Member since ${created}`;

  const faceStatus = document.getElementById('face-status');
  const statFace = document.getElementById('stat-face');
  const statSecurity = document.getElementById('stat-security');

  if (user.has_face_embedding) {
    faceStatus.innerHTML = '<span class="badge badge-success">✓ Face Registered</span>';
    statFace.textContent = 'Yes';
    statFace.classList.add('success');
    statSecurity.textContent = 'Enhanced';
    statSecurity.classList.add('success');
    document.getElementById('register-face-btn').textContent = '🔄 Re-register Face';
  } else {
    faceStatus.innerHTML = '<span class="badge badge-warning">⚠ No Face Registered</span>';
    statFace.textContent = 'No';
    statSecurity.textContent = 'Standard';
  }
}

loadProfile();

// ─── Face Registration ─────────────────────────────
let faceStream = null;

async function openFaceRegister() {
  document.getElementById('face-modal').classList.add('active');
  try {
    faceStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' }
    });
    document.getElementById('face-video').srcObject = faceStream;
  } catch {
    showAlert('face-alert', 'Camera access denied. Please allow camera permissions.', 'error');
  }
}

function closeFaceModal() {
  document.getElementById('face-modal').classList.remove('active');
  if (faceStream) {
    faceStream.getTracks().forEach(t => t.stop());
    faceStream = null;
  }
  document.getElementById('face-video').srcObject = null;
}

async function captureFace() {
  const video = document.getElementById('face-video');
  const canvas = document.getElementById('face-canvas');
  const btn = document.getElementById('capture-btn');

  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0);

  btn.innerHTML = '<span class="spinner"></span> Registering...';
  btn.disabled = true;

  canvas.toBlob(async (blob) => {
    const res = await api.registerFace(blob);
    if (res.ok) {
      showAlert('face-alert', 'Face registered successfully!', 'success');
      setTimeout(() => {
        closeFaceModal();
        loadProfile();
      }, 1200);
    } else {
      showAlert('face-alert', res.data?.detail || 'Face registration failed', 'error');
    }
    btn.innerHTML = '📸 Capture & Register';
    btn.disabled = false;
  }, 'image/jpeg', 0.9);
}

// ─── Edit Profile ──────────────────────────────────
function openEditModal() {
  document.getElementById('edit-modal').classList.add('active');
  document.getElementById('edit-email').value = '';
  document.getElementById('edit-password').value = '';
}

function closeEditModal() {
  document.getElementById('edit-modal').classList.remove('active');
}

document.getElementById('edit-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('edit-email').value.trim();
  const password = document.getElementById('edit-password').value;

  const data = {};
  if (email) data.email = email;
  if (password) data.password = password;

  if (Object.keys(data).length === 0) {
    showAlert('alert-area', 'No changes to save', 'info');
    closeEditModal();
    return;
  }

  const res = await api.updateProfile(data);
  if (res.ok) {
    showAlert('alert-area', 'Profile updated!', 'success');
    if (email) {
      // Re-login to get new token with updated email
      const loginRes = await api.login(email, password || prompt('Enter your password to re-authenticate:'));
      if (loginRes.ok) {
        api.saveTokens(loginRes.data.access_token, loginRes.data.refresh_token);
        localStorage.setItem('user_email', email);
      }
    }
    closeEditModal();
    loadProfile();
  } else {
    showAlert('alert-area', res.data?.detail || 'Update failed', 'error');
  }
});

// ─── Delete Account ────────────────────────────────
async function confirmDelete() {
  if (!confirm('Are you sure you want to delete your account? This cannot be undone.')) return;
  const res = await api.deleteProfile();
  if (res.ok || res.status === 204) {
    alert('Account deleted.');
    logout();
  } else {
    showAlert('alert-area', res.data?.detail || 'Delete failed', 'error');
  }
}
