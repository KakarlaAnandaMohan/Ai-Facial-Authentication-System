from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select

from app.models import User
from app.schemas import AnalyticsResponse
from app.database import get_db

router = APIRouter()

@router.get("/usage", response_model=AnalyticsResponse)
async def get_usage_statistics(db: AsyncSession = Depends(get_db)):
    total_res = await db.execute(select(func.count(User.id)))
    total_users = total_res.scalar_one_or_none() or 0
    
    faces_res = await db.execute(select(func.count(User.id)).where(User.face_embedding.isnot(None)))
    users_with_faces = faces_res.scalar_one_or_none() or 0
    
    return AnalyticsResponse(
        total_users=total_users,
        users_with_faces=users_with_faces,
        system_status="operational",
    )
