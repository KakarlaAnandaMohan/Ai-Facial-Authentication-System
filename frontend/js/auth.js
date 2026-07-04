redirectIfAuth();

// Show registration success message if redirected from register.html
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('registered') === 'true') {
  showAlert('alert-area', 'Account created successfully! Please sign in below.', 'success');
}

// ─── Login Form ────────────────────────────────────
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const btn = document.getElementById('login-btn');

  btn.innerHTML = '<span class="spinner"></span> Signing in...';
  btn.disabled = true;

  try {
    const res = await api.login(email, password);
    if (res.ok) {
      api.saveTokens(res.data.access_token, res.data.refresh_token);
      localStorage.setItem('user_email', email);
      window.location.href = 'dashboard.html';
    } else {
      showAlert('alert-area', res.data?.detail || 'Login failed', 'error');
      btn.innerHTML = 'Sign In';
      btn.disabled = false;
    }
  } catch (err) {
    console.error(err);
    showAlert('alert-area', 'Cannot connect to backend server. Make sure uvicorn is running on port 8080.', 'error');
    btn.innerHTML = 'Sign In';
    btn.disabled = false;
  }
});

// ─── Face Login Modal ──────────────────────────────
let faceStream = null;

async function openFaceLogin() {
  const modal = document.getElementById('face-modal');
  modal.classList.add('active');

  try {
    faceStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' }
    });
    document.getElementById('face-video').srcObject = faceStream;
  } catch (err) {
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

async function captureFaceLogin() {
  const video = document.getElementById('face-video');
  const canvas = document.getElementById('face-canvas');
  const btn = document.getElementById('capture-login-btn');

  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0);

  btn.innerHTML = '<span class="spinner"></span> Authenticating...';
  btn.disabled = true;

  canvas.toBlob(async (blob) => {
    const email = document.getElementById('face-email').value.trim() || null;
    const res = await api.loginFace(blob, email);

    if (res.ok) {
      api.saveTokens(res.data.access_token, res.data.refresh_token);
      if (email) localStorage.setItem('user_email', email);
      closeFaceModal();
      window.location.href = 'dashboard.html';
    } else {
      showAlert('face-alert', res.data?.detail || 'Face authentication failed', 'error');
      btn.innerHTML = '📸 Capture & Login';
      btn.disabled = false;
    }
  }, 'image/jpeg', 0.9);
}
