from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    title: str
    description: str
    experience_years: List[int] = Field(..., min_items=2, max_items=2)
    education_required: Dict[str, str]
    expires_at: Optional[datetime]
    salary: Optional[float]
    location: Optional[str]
    skills_required: List[str]
    company_name: str
    company_industry: str
    company_size: Optional[str]

    def to_embedding_text(self) -> str:
        """Text representation of job for embedding generation"""

        experience = " to ".join(map(str, self.experience_years))

        education = ", ".join(
            f"{k}: {v}" for k, v in self.education_required.items()
        )

        skills = ", ".join(self.skills_required)

        return f"""
        Job Title: {self.title}
        Industry: {self.company_industry}
        Required Experience: {experience} years
        Required Education: {education}
        Required Skills: {skills}

        Job Description:
        {self.description}
        """.strip()


class JobCreate(JobBase):
    class Config:
        from_attributes = True

class JobUpdate(JobBase):
    pass


class JobResponse(JobBase):
    id: int
    created_at: datetime
    is_expired: bool
    updated_at: datetime
    class Config:
        from_attributes = True

