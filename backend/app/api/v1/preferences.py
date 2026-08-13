from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.schemas.preferences import JobPreferencesUpdate, JobPreferencesResponse
from app.services.preferences import get_or_create_user_preferences, create_or_update_user_preferences

router = APIRouter(prefix="/preferences", tags=["Job Preferences"])

@router.get("", response_model=JobPreferencesResponse, summary="Get Current User Job Preferences")
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves the authenticated user's job search & auto-apply preferences."""
    return get_or_create_user_preferences(db, current_user)

@router.put("", response_model=JobPreferencesResponse, summary="Update Current User Job Preferences")
def update_preferences(
    prefs_in: JobPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Updates the authenticated user's job search & auto-apply preferences."""
    return create_or_update_user_preferences(db, current_user, prefs_in)

@router.post("", response_model=JobPreferencesResponse, summary="Create/Update Current User Job Preferences")
def create_preferences(
    prefs_in: JobPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates or updates the authenticated user's job search & auto-apply preferences."""
    return create_or_update_user_preferences(db, current_user, prefs_in)
