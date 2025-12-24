from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel
from app.schemas.jobs import JobResponse


class MatchingFactors(BaseModel):
    skills_match: float
    experience_match: float
    education_match: float
    semantic_similarity: float

class JobRecommendationBase(BaseModel):
    job: JobResponse
    match_score: float
    matching_factors: MatchingFactors
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: str
    # created_at: datetime

    class Config:
        from_attributes = True


class JobRecommendationResponse(JobRecommendationBase):
    pass