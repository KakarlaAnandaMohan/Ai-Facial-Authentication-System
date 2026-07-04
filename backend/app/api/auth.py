import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User
from app.schemas import AuthRegister, AuthLogin, TokenResponse
from app.database import get_db
from app.core import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.services import extract_embedding, encrypt_embedding

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Verify the bearer token has role=admin.

    Unlike get_current_user, the admin email does NOT need to exist in the
    users table — this allows system-level admin tokens (e.g. superadmin@system.local).
    """
    try:
        payload = decode_token(token)
        if payload.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
        return payload  # return the decoded claims; handlers only need the auth gate
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: AuthRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    access_token = create_access_token({"sub": user.email, "role": "user"})
    refresh_token = create_refresh_token({"sub": user.email})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/login", response_model=TokenResponse)
async def login(payload: AuthLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalars().first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user.email, "role": "user"})
    refresh_token = create_refresh_token({"sub": user.email})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/register-with-face", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_with_face(
    email: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
        
    try:
        raw_emb = extract_embedding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Face extraction failed: {e}")
        
    encrypted_emb = encrypt_embedding(raw_emb)
    
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        password_hash=get_password_hash(password),
        face_embedding=encrypted_emb,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    access_token = create_access_token({"sub": user.email, "role": "user"})
    refresh_token = create_refresh_token({"sub": user.email})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
