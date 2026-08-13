import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.preferences import JobPreferences
from app.schemas.preferences import JobPreferencesCreate, JobPreferencesUpdate, JobPreferencesResponse

def _parse_json_list(raw_val: Optional[str]) -> List[str]:
    """Helper to safely parse JSON list or comma-separated string into a list of strings."""
    if not raw_val:
        return []
    try:
        data = json.loads(raw_val)
        if isinstance(data, list):
            return [str(x) for x in data]
        return [str(data)]
    except Exception:
        return [x.strip() for x in raw_val.split(",") if x.strip()]

def _format_preferences_response(prefs: JobPreferences) -> JobPreferencesResponse:
    """Helper to convert JobPreferences model to JobPreferencesResponse Pydantic schema."""
    return JobPreferencesResponse(
        id=prefs.id,
        user_id=prefs.user_id,
        auto_apply_enabled=bool(prefs.auto_apply_enabled),
        daily_apply_limit=prefs.daily_apply_limit if prefs.daily_apply_limit is not None else 10,
        desired_job_titles=_parse_json_list(prefs.desired_job_titles),
        preferred_industries=_parse_json_list(prefs.preferred_industries),
        min_salary=prefs.min_salary,
        created_at=prefs.created_at,
        updated_at=prefs.updated_at
    )

def get_or_create_user_preferences(db: Session, user: User) -> JobPreferencesResponse:
    """Retrieves or initializes the authenticated user's job search preferences."""
    prefs = db.query(JobPreferences).filter(JobPreferences.user_id == user.id).first()
    if not prefs:
        prefs = JobPreferences(
            user_id=user.id,
            auto_apply_enabled=False,
            daily_apply_limit=10,
            desired_job_titles=json.dumps([]),
            preferred_industries=json.dumps([]),
            min_salary=None
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return _format_preferences_response(prefs)

def create_or_update_user_preferences(
    db: Session,
    user: User,
    prefs_in: JobPreferencesUpdate
) -> JobPreferencesResponse:
    """Creates or updates the authenticated user's job search preferences."""
    prefs = db.query(JobPreferences).filter(JobPreferences.user_id == user.id).first()
    if not prefs:
        prefs = JobPreferences(
            user_id=user.id,
            auto_apply_enabled=False,
            daily_apply_limit=10,
            desired_job_titles=json.dumps([]),
            preferred_industries=json.dumps([])
        )
        db.add(prefs)

    update_data = prefs_in.model_dump(exclude_unset=True) if hasattr(prefs_in, 'model_dump') else prefs_in.dict(exclude_unset=True)

    if "desired_job_titles" in update_data:
        titles_val = update_data.pop("desired_job_titles")
        if titles_val is not None:
            prefs.desired_job_titles = json.dumps(titles_val)

    if "preferred_industries" in update_data:
        industries_val = update_data.pop("preferred_industries")
        if industries_val is not None:
            prefs.preferred_industries = json.dumps(industries_val)

    for field, val in update_data.items():
        if hasattr(prefs, field):
            setattr(prefs, field, val)

    db.commit()
    db.refresh(prefs)
    return _format_preferences_response(prefs)
