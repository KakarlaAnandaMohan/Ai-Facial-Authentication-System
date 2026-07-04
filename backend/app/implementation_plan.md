# Implementation Plan – Backend Completion

## Goal
Finish the backend for the AI‑Based Facial Authentication System by adding:
1. Admin and analytics routers (already created).
2. Alembic migration for the `users` table.
3. Real face‑embedding extraction using InsightFace and AES‑256 encryption.
4. Configuration for encryption keys and optional admin role.
5. Unit tests for auth, face, and user profile routes.
6. Server verification.

## Open Questions (need your confirmation)
- **Encryption Key**: Store in env var `ENCRYPTION_KEY` (base64‑encoded 32‑byte key) or use a secret manager?
- **Admin Role Claim**: Add `role: "admin"` to JWT at token creation, or create a separate admin‑login endpoint?
- **InsightFace Model**: Use default `arcface_r100_v1` from the `insightface` package (requires `torch`) or a lighter ONNX model?
- **Analytics Data**: Keep placeholder stats or create a `login_events` table now?
- **Test Database**: In‑memory SQLite (`sqlite+aiosqlite:///:memory:`) or temporary PostgreSQL container?

Please answer these so we can proceed.

## Proposed Changes
### 1. Settings (`app/core/config.py`)
- Add `ENCRYPTION_KEY: str` (Base64) and optional `ADMIN_PASSWORD: str`.
- Provide helper to decode key: `ENCRYPTION_KEY_BYTES = base64.b64decode(ENCRYPTION_KEY)`.

### 2. Security (`app/core/security.py`)
- Extend `create_access_token(data: dict, expires_delta: timedelta | None = None, role: str | None = None)` to embed `role` claim when provided.
- Add `create_admin_token(email: str)` utility.
- Ensure `decode_token` returns the full payload.

### 3. Alembic Migration
- Add `backend/alembic/` with `alembic.ini`, `env.py`, and `versions/`.
- Migration `xxxx_create_users_table.py`:
  ```python
  def upgrade():
      op.create_table(
          "users",
          sa.Column("id", sa.String(), primary_key=True),
          sa.Column("email", sa.String(), nullable=False, unique=True),
          sa.Column("password_hash", sa.String(), nullable=False),
          sa.Column("face_embedding", sa.LargeBinary(), nullable=True),
          sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
          sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
      )
  def downgrade():
      op.drop_table("users")
  ```
- Run `alembic upgrade head` after creating.

### 4. Face Service (`backend/app/services/face_service.py`)
```python
import base64, numpy as np
from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from insightface.app import FaceAnalysis
from app.core.config import settings

# Load model once
_face_app = FaceAnalysis(name='buffalo_l', providers=['CPU'])
_face_app.prepare(ctx_id=0, det_thresh=0.5)

def _load_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    return np.array(img)

def extract_embedding(image_bytes: bytes) -> bytes:
    img = _load_image(image_bytes)
    faces = _face_app.get(img)
    if not faces:
        raise ValueError('No face detected')
    embedding = faces[0].embedding  # np.ndarray shape (512,)
    return embedding.tobytes()

def encrypt_embedding(embedding: bytes) -> bytes:
    key = settings.ENCRYPTION_KEY_BYTES
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, embedding, None)
    return nonce + ct  # prepend nonce

def decrypt_embedding(ciphertext: bytes) -> bytes:
    key = settings.ENCRYPTION_KEY_BYTES
    nonce, ct = ciphertext[:12], ciphertext[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None)
```

### 5. Update `api/face.py`
- Replace placeholder `_extract_face_embedding` with `face_service.extract_embedding`.
- Store encrypted bytes: `current_user.face_embedding = face_service.encrypt_embedding(raw_emb)`.
- During login, decrypt stored embedding, compute cosine similarity:
  ```python
  def cosine(a, b):
      a, b = np.frombuffer(a, dtype=np.float32), np.frombuffer(b, dtype=np.float32)
      return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
  ```
- Use threshold `0.8` (configurable via `settings.FACE_THRESHOLD`).

### 6. Unit Tests (`backend/tests/`)
- **conftest.py** – fixture to create an async SQLite DB, run Alembic migrations, provide `AsyncClient`.
- **test_auth.py** – registration, login, token validation.
- **test_face.py** – generate a tiny synthetic face image (solid color) to feed into the service; mock `face_service` if needed.
- **test_user.py** – read, update, delete profile.
- **test_admin.py** – list and delete users using an admin token.
- **test_analytics.py** – ensure endpoint returns the three keys.
- Add `pytest.ini` with `asyncio_mode = auto`.

### 7. Server Verification
- Run `uvicorn backend.app.main:app --reload`.
- Quick sanity checks (curl or httpx) for each route to confirm correct status codes and JWT handling.

## Verification Plan
1. **Automated** – `pytest -q` must pass all tests (target >90% coverage for auth, face, user).
2. **Manual** – Start the server, perform:
   - `POST /auth/register` → 201, token.
   - `POST /auth/login` → 200, token.
   - `POST /face/register` (with token) → 200.
   - `POST /face/login` → 200, token.
   - `GET /user/me` → 200.
   - `GET /admin/users` with admin token → 200.
   - `GET /analytics/usage` → 200 JSON.
3. **Logs** – Verify security headers are present in responses.

---
**Please answer the open questions or confirm the defaults** so I can proceed with creating the files, migrations, services, tests, and running verification.
