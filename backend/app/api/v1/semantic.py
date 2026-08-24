from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.resume import get_user_resume_by_id
from app.services.jobs import get_jobs_from_db
from app.services.resume_chunking import (
    index_user_resume_vectors,
    search_resume_semantic
)
from app.services.job_indexing import (
    index_all_jobs,
    search_jobs_by_query_semantic,
    retrieve_matched_jobs_for_resume
)

router = APIRouter(prefix="/semantic", tags=["Semantic Search & Vector DB (Phase 8)"])

class SemanticSearchQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    resume_id: Optional[int] = Field(None, description="Optional resume ID filter")
    limit: Optional[int] = Field(5, ge=1, le=50, description="Max results limit")

class SemanticJobSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    limit: Optional[int] = Field(5, ge=1, le=50, description="Max results limit")

@router.post("/resumes/{resume_id}/index", status_code=status.HTTP_200_OK)
def index_resume_endpoint(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Indexes or re-indexes an authenticated user's resume into Qdrant Cloud idempotently.
    Enforces ownership isolation.
    """
    resume = get_user_resume_by_id(db, current_user, resume_id)
    if not resume.extracted_text or not resume.extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume extracted text is empty. Cannot index empty content."
        )
        
    try:
        res = index_user_resume_vectors(
            user_id=current_user.id,
            resume_id=resume.id,
            extracted_text=resume.extracted_text
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index resume vectors: {str(e)}"
        )

@router.post("/resumes/search", status_code=status.HTTP_200_OK)
def search_resumes_semantic_endpoint(
    request: SemanticSearchQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Performs semantic similarity search strictly over the authenticated user's resume vectors."""
    try:
        results = search_resume_semantic(
            user_id=current_user.id,
            query=request.query,
            limit=request.limit or 5,
            resume_id=request.resume_id
        )
        return {"query": request.query, "user_id": current_user.id, "results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic resume search failed: {str(e)}"
        )

@router.post("/jobs/index-all", status_code=status.HTTP_200_OK)
def index_all_jobs_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Indexes static job listings into Qdrant Cloud (`hireagent_jobs` collection) idempotently."""
    try:
        # Retrieve all jobs from SQLite database
        job_data = get_jobs_from_db(search=None, role=None, limit=200, offset=0)
        jobs_list = job_data.get("jobs", [])
        
        res = index_all_jobs(jobs_list)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index jobs into Qdrant Cloud: {str(e)}"
        )

@router.post("/jobs/search", status_code=status.HTTP_200_OK)
def search_jobs_semantic_endpoint(
    request: SemanticJobSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Performs semantic similarity search across indexed job vectors."""
    try:
        results = search_jobs_by_query_semantic(
            query_text=request.query,
            limit=request.limit or 5
        )
        return {"query": request.query, "results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic job search failed: {str(e)}"
        )

@router.get("/resumes/{resume_id}/matched-jobs", status_code=status.HTTP_200_OK)
def get_resume_matched_jobs_semantic_endpoint(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves job listings semantically matched against the authenticated user's resume vectors."""
    resume = get_user_resume_by_id(db, current_user, resume_id)
    try:
        results = retrieve_matched_jobs_for_resume(
            user_id=current_user.id,
            resume_id=resume.id,
            top_k=5
        )
        return {
            "user_id": current_user.id,
            "resume_id": resume.id,
            "filename": resume.filename,
            "matched_jobs": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic resume-to-job retrieval failed: {str(e)}"
        )
