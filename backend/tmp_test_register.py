# temporary test script to verify registration endpoint with new hashing scheme
import asyncio
from httpx import AsyncClient
from app.main import app

async def main():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {"email": "temp@example.com", "password": "StrongPassword123"}
        resp = await client.post("/api/auth/register", json=payload)
        print("Status:", resp.status_code)
        print(resp.json())

if __name__ == "__main__":
    asyncio.run(main())
