import pytest

@pytest.mark.asyncio
async def test_user_profile_crud(client):
    reg_data = {"email": "crud@example.com", "password": "StrongPassword123"}
    reg_res = await client.post("/api/auth/register", json=reg_data)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get profile
    res = await client.get("/api/user/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "crud@example.com"

    # Update profile
    update_data = {"email": "crud_updated@example.com"}
    up_res = await client.put("/api/user/me", json=update_data, headers=headers)
    assert up_res.status_code == 200
    assert up_res.json()["email"] == "crud_updated@example.com"

    # Re-login with updated email to get a valid token
    login_data = {"email": "crud_updated@example.com", "password": "StrongPassword123"}
    login_res = await client.post("/api/auth/login", json=login_data)
    assert login_res.status_code == 200
    new_token = login_res.json()["access_token"]
    new_headers = {"Authorization": f"Bearer {new_token}"}

    # Delete profile
    del_res = await client.delete("/api/user/me", headers=new_headers)
    assert del_res.status_code == 204
