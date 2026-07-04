from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User
from app.schemas import UserResponse, UserUpdate
from app.database import get_db
from app.core import get_password_hash
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        has_face_embedding=current_user.face_embedding is not None,
        created_at=current_user.created_at,
    )

@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.email and payload.email != current_user.email:
        # Check uniqueness
        res = await db.execute(select(User).where(User.email == payload.email))
        if res.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        current_user.email = payload.email
    
    if payload.password:
        current_user.password_hash = get_password_hash(payload.password)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        has_face_embedding=current_user.face_embedding is not None,
        created_at=current_user.created_at,
    )

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.delete(current_user)
    await db.commit()
