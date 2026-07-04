import pytest
from app.core import create_admin_token

@pytest.mark.asyncio
async def test_admin_list_and_delete_users(client):
    # Create normal user
    reg_data = {"email": "victim@example.com", "password": "StrongPassword123"}
    await client.post("/api/auth/register", json=reg_data)

    # Normal user cannot access admin routes
    norm_token = (await client.post("/api/auth/login", json=reg_data)).json()["access_token"]
    norm_headers = {"Authorization": f"Bearer {norm_token}"}
    forbidden_res = await client.get("/api/admin/users", headers=norm_headers)
    assert forbidden_res.status_code == 403

    # Admin access
    admin_token = create_admin_token("superadmin@system.local")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    list_res = await client.get("/api/admin/users", headers=admin_headers)
    assert list_res.status_code == 200
    users = list_res.json()
    assert len(users) >= 1
    target = [u for u in users if u["email"] == "victim@example.com"][0]

    # Admin delete user
    del_res = await client.delete(f"/api/admin/users/{target['id']}", headers=admin_headers)
    assert del_res.status_code == 204
