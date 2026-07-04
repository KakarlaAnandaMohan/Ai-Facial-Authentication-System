from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User
from app.schemas import TokenResponse
from app.database import get_db
from app.core import settings, create_access_token, create_refresh_token
from app.api.auth import get_current_user
from app.services import extract_embedding, encrypt_embedding, decrypt_embedding, cosine_similarity

router = APIRouter()

@router.post("/register", status_code=status.HTTP_200_OK)
async def register_face(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    
    try:
        raw_emb = extract_embedding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Face extraction failed: {e}")
    
    encrypted_emb = encrypt_embedding(raw_emb)
    current_user.face_embedding = encrypted_emb
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return {"status": "success", "message": "Face embedding registered successfully"}

@router.post("/login", response_model=TokenResponse)
async def login_face(
    file: UploadFile = File(...),
    email: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    
    try:
        query_emb = extract_embedding(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Face extraction failed: {e}")
    
    if email:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user or not user.face_embedding:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Face authentication failed")
        
        try:
            stored_emb = decrypt_embedding(user.face_embedding)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Decryption error")
        
        sim = cosine_similarity(query_emb, stored_emb)
        if sim < settings.FACE_THRESHOLD:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Face mismatch (similarity: {sim:.2f})")
        matched_user = user
    else:
        # Search among all users with face embeddings
        result = await db.execute(select(User).where(User.face_embedding.isnot(None)))
        users = result.scalars().all()
        best_user = None
        best_sim = -1.0
        for u in users:
            try:
                stored_emb = decrypt_embedding(u.face_embedding)
                sim = cosine_similarity(query_emb, stored_emb)
                if sim > best_sim:
                    best_sim = sim
                    best_user = u
            except Exception:
                continue
        
        if not best_user or best_sim < settings.FACE_THRESHOLD:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Face not recognized")
        matched_user = best_user

    access_token = create_access_token({"sub": matched_user.email, "role": "user"})
    refresh_token = create_refresh_token({"sub": matched_user.email})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
