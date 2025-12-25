from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Float, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.config import settings
from app.database.db import Base    


from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

class JobRecommendation(Base):
    __tablename__ = "job_recommendations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    cv_id = Column(Integer, ForeignKey("cvs.id"), nullable=False, index=True)

    match_score = Column(Float, nullable=False)

    matching_factors = Column(JSONB, nullable=False)
    matched_skills = Column(JSONB, nullable=False)
    missing_skills = Column(JSONB, nullable=False)

    explanation = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=func.now())

    user = relationship("User")
    job = relationship("Job")
    cv = relationship("CV")

    def __repr__(self):
        return f"<JobRecommendation job_id={self.job_id} score={self.match_score}>"
