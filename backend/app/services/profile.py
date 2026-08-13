import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse

def _format_profile_response(profile: UserProfile) -> UserProfileResponse:
    """Helper function to format UserProfile SQLAlchemy model into Pydantic UserProfileResponse."""
    locations: List[str] = []
    if profile.preferred_locations:
        try:
            locations = json.loads(profile.preferred_locations)
            if not isinstance(locations, list):
                locations = [str(locations)]
        except Exception:
            locations = [loc.strip() for loc in profile.preferred_locations.split(",") if loc.strip()]

    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        target_role=profile.target_role,
        experience_level=profile.experience_level,
        preferred_locations=locations,
        work_mode_preference=profile.work_mode_preference,
        employment_type=profile.employment_type,
        min_match_score=profile.min_match_score if profile.min_match_score is not None else 70.0,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

def get_or_create_user_profile(db: Session, user: User) -> UserProfileResponse:
    """Retrieves or initializes a user's career profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(
            user_id=user.id,
            target_role=None,
            experience_level=None,
            preferred_locations=json.dumps([]),
            work_mode_preference=None,
            employment_type=None,
            min_match_score=70.0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return _format_profile_response(profile)

def create_or_update_user_profile(
    db: Session,
    user: User,
    profile_in: UserProfileUpdate
) -> UserProfileResponse:
    """Creates or updates the authenticated user's career profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True) if hasattr(profile_in, 'model_dump') else profile_in.dict(exclude_unset=True)

    if "preferred_locations" in update_data:
        locations_val = update_data.pop("preferred_locations")
        if locations_val is not None:
            profile.preferred_locations = json.dumps(locations_val)

    for field, val in update_data.items():
        if hasattr(profile, field):
            setattr(profile, field, val)

    db.commit()
    db.refresh(profile)
    return _format_profile_response(profile)
