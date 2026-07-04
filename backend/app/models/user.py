from sqlalchemy import Column, String, LargeBinary, DateTime, func
import uuid

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    # face_embedding stored encrypted as binary; placeholder length 1024 bytes
    face_embedding = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
