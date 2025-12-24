from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Float, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.database.db import Base    

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, index=True, nullable=False)
    experience_years = Column(ARRAY(Integer), nullable=False)
    is_expired = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    salary = Column(Float)
    location = Column(String, nullable=False)
    education_required = Column(JSON, nullable=False)
    skills_required = Column(ARRAY(String), nullable=False)
    company_name = Column(String, nullable=False)
    company_industry = Column(String, nullable=False)
    company_size = Column(String)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    embeddings = relationship(
        "JobEmbedding",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'<JOB {self.id}, {self.title}, {self.description[:20]}...>'
    


class JobEmbedding(Base):
    __tablename__ = "job_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=False)
    model_name = Column(String, nullable=False)

    created_at = Column(DateTime, default=func.now())

    job = relationship("Job", back_populates="embeddings")