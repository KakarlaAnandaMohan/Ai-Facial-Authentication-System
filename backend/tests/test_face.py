import pytest

@pytest.mark.asyncio
async def test_face_registration_and_login(client):
    # Register user first
    reg_data = {"email": "face@example.com", "password": "StrongPassword123"}
    reg_res = await client.post("/api/auth/register", json=reg_data)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Register face embedding using dummy image bytes
    dummy_image = b"fake_image_bytes_for_testing_1234567890"
    files = {"file": ("face.jpg", dummy_image, "image/jpeg")}
    face_reg_res = await client.post("/api/face/register", files=files, headers=headers)
    assert face_reg_res.status_code == 200

    # Verify profile now reports has_face_embedding=True
    prof_res = await client.get("/api/user/me", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["has_face_embedding"] is True

    # Face Login with same dummy image and email
    files_login = {"file": ("face.jpg", dummy_image, "image/jpeg")}
    data_login = {"email": "face@example.com"}
    login_res = await client.post("/api/face/login", files=files_login, data=data_login)
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
