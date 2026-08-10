from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ResumeSummary(BaseModel):
    id: int
    filename: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResumeDetail(BaseModel):
    id: int
    filename: str
    extracted_text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
