from typing import Optional, List
from pydantic import BaseModel

class JobResponse(BaseModel):
    id: Optional[int] = None
    job_title: str
    company: str
    required_skills: str
    experience_level: Optional[str] = None
    job_role: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    total: int
    jobs: List[JobResponse]
