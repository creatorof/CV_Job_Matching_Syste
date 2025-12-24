from sqlalchemy.sql import func
from sqlalchemy import Text, Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database.db import Base  
from pgvector.sqlalchemy import Vector
from app.core.config import settings

class CV(Base):
    __tablename__ = 'cvs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)
    location = Column(JSONB, index=True)  
    summary = Column(Text, nullable=True)
    work = Column(JSONB)  
    education = Column(JSONB) 
    skills = Column(JSONB) 
    languages = Column(JSONB)  
    certifications = Column(JSONB) 
    category = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())
    

    user = relationship('User', back_populates='cvs')
    embeddings = relationship(
            "CVEmbedding",
            back_populates="cv",
            cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'<CV {self.id}, {self.name}, {self.email}>'


class CVEmbedding(Base):
    __tablename__ = "cv_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    cv_id = Column(Integer, ForeignKey("cvs.id", ondelete="CASCADE"), nullable=False)

    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=False) 
    created_at = Column(DateTime, default=func.now())

    cv = relationship("CV", back_populates="embeddings")

    def __repr__(self):
        return f'<CVEmbedding {self.id}, CV_ID: {self.cv_id}>'