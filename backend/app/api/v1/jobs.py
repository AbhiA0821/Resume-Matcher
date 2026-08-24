from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.job import JobListResponse
from app.services.jobs import get_jobs_from_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=JobListResponse, summary="List Job Opportunities")
def list_jobs(
    search: Optional[str] = Query(None, description="Search term for job title, skills, or description"),
    role: Optional[str] = Query(None, description="Target job role filter"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of job listings to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Fetches job listings from underlying database with search and role filtering."""
    return get_jobs_from_db(search=search, role=role, limit=limit, offset=offset)
