from .auth import router as auth_router
from .face import router as face_router
from .user import router as user_router
from .admin import router as admin_router
from .analytics import router as analytics_router

__all__ = [
    "auth_router",
    "face_router",
    "user_router",
    "admin_router",
    "analytics_router",
]
