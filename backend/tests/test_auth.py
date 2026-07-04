import pytest

@pytest.mark.asyncio
async def test_register_and_login(client):
    # Register
    reg_data = {"email": "test@example.com", "password": "StrongPassword123"}
    response = await client.post("/api/auth/register", json=reg_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Register duplicate email
    dup_res = await client.post("/api/auth/register", json=reg_data)
    assert dup_res.status_code == 400

    # Login
    login_res = await client.post("/api/auth/login", json=reg_data)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
