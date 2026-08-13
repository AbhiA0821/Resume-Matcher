from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class UserProfileBase(BaseModel):
    target_role: Optional[str] = Field(None, max_length=255, description="Target job title or role (e.g. Senior AI Engineer)")
    experience_level: Optional[str] = Field(None, max_length=50, description="Experience level (e.g. Entry, Mid, Senior, Lead, Executive)")
    preferred_locations: Optional[List[str]] = Field(default_factory=list, description="List of preferred work locations")
    work_mode_preference: Optional[str] = Field(None, max_length=50, description="Work mode preference (e.g. Remote, Hybrid, On-site)")
    employment_type: Optional[str] = Field(None, max_length=50, description="Employment type (e.g. Full-time, Part-time, Contract)")
    min_match_score: Optional[float] = Field(70.0, ge=0.0, le=100.0, description="Minimum match score (0-100)")

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(BaseModel):
    target_role: Optional[str] = Field(None, max_length=255)
    experience_level: Optional[str] = Field(None, max_length=50)
    preferred_locations: Optional[List[str]] = None
    work_mode_preference: Optional[str] = Field(None, max_length=50)
    employment_type: Optional[str] = Field(None, max_length=50)
    min_match_score: Optional[float] = Field(None, ge=0.0, le=100.0)

class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    preferred_locations: List[str] = []
    work_mode_preference: Optional[str] = None
    employment_type: Optional[str] = None
    min_match_score: float = 70.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
