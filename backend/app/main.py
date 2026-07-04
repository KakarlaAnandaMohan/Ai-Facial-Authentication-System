from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.api import auth_router, face_router, user_router, admin_router, analytics_router
from app.database import engine, Base

app = FastAPI(title="Facial Authentication System", version="0.1.0")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(face_router, prefix="/api/face", tags=["face"])
app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

@app.get("/health")
async def health_check(request: Request):
    return {"status": "ok"}
