import pytest

@pytest.mark.asyncio
async def test_analytics_endpoint(client):
    res = await client.get("/api/analytics/usage")
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "users_with_faces" in data
    assert data["system_status"] == "operational"
