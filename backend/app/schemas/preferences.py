from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class JobPreferencesBase(BaseModel):
    auto_apply_enabled: bool = Field(False, description="Enable or disable automated job application preference")
    daily_apply_limit: int = Field(10, ge=1, le=100, description="Daily application quota limit")
    desired_job_titles: Optional[List[str]] = Field(default_factory=list, description="Target job titles/keywords")
    preferred_industries: Optional[List[str]] = Field(default_factory=list, description="Target industries")
    min_salary: Optional[float] = Field(None, ge=0.0, description="Minimum expected salary requirement")

class JobPreferencesCreate(JobPreferencesBase):
    pass

class JobPreferencesUpdate(BaseModel):
    auto_apply_enabled: Optional[bool] = None
    daily_apply_limit: Optional[int] = Field(None, ge=1, le=100)
    desired_job_titles: Optional[List[str]] = None
    preferred_industries: Optional[List[str]] = None
    min_salary: Optional[float] = Field(None, ge=0.0)

class JobPreferencesResponse(BaseModel):
    id: int
    user_id: int
    auto_apply_enabled: bool = False
    daily_apply_limit: int = 10
    desired_job_titles: List[str] = []
    preferred_industries: List[str] = []
    min_salary: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
