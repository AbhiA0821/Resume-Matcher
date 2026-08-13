from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.schemas.profile import UserProfileUpdate, UserProfileResponse
from app.services.profile import get_or_create_user_profile, create_or_update_user_profile

router = APIRouter(prefix="/profile", tags=["User Profile"])

@router.get("", response_model=UserProfileResponse, summary="Get Current User Profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves the authenticated user's career profile."""
    return get_or_create_user_profile(db, current_user)

@router.put("", response_model=UserProfileResponse, summary="Update Current User Profile")
def update_profile(
    profile_in: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Updates the authenticated user's career profile."""
    return create_or_update_user_profile(db, current_user, profile_in)

@router.post("", response_model=UserProfileResponse, summary="Create/Update Current User Profile")
def create_profile(
    profile_in: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates or updates the authenticated user's career profile."""
    return create_or_update_user_profile(db, current_user, profile_in)
