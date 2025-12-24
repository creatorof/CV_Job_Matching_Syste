from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Location(BaseModel):
    city: Optional[str] = None
    countryCode: Optional[str] = None
    region: Optional[str] = None

class WorkExperience(BaseModel):
    company: str
    position: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = []

class Education(BaseModel):
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    gpa: Optional[str] = None

class CVData(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: Optional[str] = Field(description="Email address")
    phone: Optional[str] = Field(description="Phone number")
    location: Optional[Location] = None
    summary: Optional[str] = Field(description="Professional summary or objective")
    work: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(description="Category of the CV, e.g., Software Engineering")


class CVBase(BaseModel):
    user_id: int
    name: str
    email: str
    phone: str
    location: Optional[Location]
    summary: str
    work: List[WorkExperience]
    education: List[Education]
    skills: List[str]
    languages: List[str]
    certifications: List[str]
    category: Optional[str]

class CVCreate(CVBase):
    pass


class CVResponse(CVBase):
    id: int

