from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="user") 
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    cvs = relationship("CV", back_populates="user")


# class UserCV(Base):
#     __tablename__ = "user_cvs"
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, index=True)
#     cv_id = Column(Integer, index=True)
#     uploaded_at = Column(DateTime, default=datetime.utcnow)
