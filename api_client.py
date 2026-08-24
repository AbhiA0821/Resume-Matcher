import os
from typing import Dict, Any, Optional, List, Tuple
import requests

def _get_api_base_url() -> str:
    url = os.environ.get("HIREAGENT_API_URL")
    if not url:
        try:
            import streamlit as st
            url = st.secrets.get("HIREAGENT_API_URL")
        except Exception:
            pass
    if not url:
        url = "http://127.0.0.1:8000"
    return url.rstrip("/")

API_BASE_URL = _get_api_base_url()

def _get_headers(token: Optional[str] = None) -> Dict[str, str]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def check_backend_health() -> bool:
    """Checks if the FastAPI backend is running and healthy."""
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return r.status_code == 200 and r.json().get("status") == "ok"
    except Exception:
        return False

# ── Auth APIs ──

def register_user(name: str, email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Registers a new HireAgent user."""
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json={"name": name, "email": email, "password": password},
            timeout=5
        )
        if r.status_code == 201:
            return r.json(), None
        return None, r.json().get("detail", "Registration failed")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def login_user(email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    """Logs in user and returns JWT access token."""
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json={"email": email, "password": password},
            timeout=5
        )
        if r.status_code == 200:
            token = r.json().get("access_token")
            return token, None
        return None, r.json().get("detail", "Invalid credentials")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def get_current_user(token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Retrieves current user details via JWT."""
    try:
        r = requests.get(
            f"{API_BASE_URL}/api/v1/auth/me",
            headers=_get_headers(token),
            timeout=5
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to fetch user details")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

# ── Resume APIs ──

def upload_resume(token: str, file_bytes: bytes, filename: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Uploads resume file to FastAPI backend."""
    try:
        files = {"file": (filename, file_bytes)}
        r = requests.post(
            f"{API_BASE_URL}/api/v1/resumes",
            headers=_get_headers(token),
            files=files,
            timeout=15
        )
        if r.status_code == 201:
            return r.json(), None
        return None, r.json().get("detail", "Resume upload failed")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def get_user_resumes(token: str) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """Fetches user's saved resumes."""
    try:
        r = requests.get(
            f"{API_BASE_URL}/api/v1/resumes",
            headers=_get_headers(token),
            timeout=5
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to fetch resumes")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def get_resume_detail(token: str, resume_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Fetches specific resume details."""
    try:
        r = requests.get(
            f"{API_BASE_URL}/api/v1/resumes/{resume_id}",
            headers=_get_headers(token),
            timeout=5
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to fetch resume details")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def delete_resume(token: str, resume_id: int) -> Tuple[bool, Optional[str]]:
    """Deletes specific resume."""
    try:
        r = requests.delete(
            f"{API_BASE_URL}/api/v1/resumes/{resume_id}",
            headers=_get_headers(token),
            timeout=5
        )
        if r.status_code == 200:
            return True, None
        return False, r.json().get("detail", "Failed to delete resume")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# ── Profile APIs ──

def get_user_profile(token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Fetches user's career profile."""
    try:
        r = requests.get(
            f"{API_BASE_URL}/api/v1/profile",
            headers=_get_headers(token),
            timeout=5
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to fetch user profile")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def update_user_profile(token: str, profile_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Updates user's career profile."""
    try:
        r = requests.put(
            f"{API_BASE_URL}/api/v1/profile",
            headers=_get_headers(token),
            json=profile_data,
            timeout=5
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to update profile")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

# ── Job Preferences APIs ──

def get_user_preferences(token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Fetches user's job search & auto-apply preferences."""
    try:
        r = requests.get(
            f"{API_BASE_URL}/api/v1/preferences",
            headers=_get_headers(token),
            timeout=5
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to fetch job preferences")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def update_user_preferences(token: str, prefs_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Updates user's job search & auto-apply preferences."""
    try:
        r = requests.put(
            f"{API_BASE_URL}/api/v1/preferences",
            headers=_get_headers(token),
            json=prefs_data,
            timeout=5
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to update job preferences")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

# ── Jobs APIs ──

def get_jobs(
    token: Optional[str] = None,
    search: Optional[str] = None,
    role: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Fetches job listings from FastAPI backend with optional search and role filtering."""
    try:
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if search:
            params["search"] = search
        if role:
            params["role"] = role
        r = requests.get(
            f"{API_BASE_URL}/api/v1/jobs",
            headers=_get_headers(token),
            params=params,
            timeout=5
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to fetch jobs")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

# ── Semantic & Vector Search APIs (Phase 8) ──

def index_resume(token: str, resume_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Indexes or re-indexes user's resume into Qdrant Cloud."""
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/semantic/resumes/{resume_id}/index",
            headers=_get_headers(token),
            timeout=30
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to index resume vectors")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def search_resume_semantic(
    token: str,
    query: str,
    limit: int = 5,
    resume_id: Optional[int] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Performs semantic vector search across authenticated user's resume chunks."""
    try:
        payload: Dict[str, Any] = {"query": query, "limit": limit}
        if resume_id is not None:
            payload["resume_id"] = resume_id
        r = requests.post(
            f"{API_BASE_URL}/api/v1/semantic/resumes/search",
            headers=_get_headers(token),
            json=payload,
            timeout=15
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to search resume vectors")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def index_all_jobs_semantic(token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Indexes static job listings into Qdrant Cloud."""
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/semantic/jobs/index-all",
            headers=_get_headers(token),
            timeout=60
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to index jobs into Qdrant")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def search_jobs_semantic(token: str, query: str, limit: int = 5) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Performs semantic vector search across indexed job listings."""
    try:
        payload = {"query": query, "limit": limit}
        r = requests.post(
            f"{API_BASE_URL}/api/v1/semantic/jobs/search",
            headers=_get_headers(token),
            json=payload,
            timeout=15
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to search jobs vector index")
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def get_resume_matched_jobs_semantic(token: str, resume_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Retrieves job listings semantically matched against candidate resume vectors."""
    try:
        r = requests.get(
            f"{API_BASE_URL}/api/v1/semantic/resumes/{resume_id}/matched-jobs",
            headers=_get_headers(token),
            timeout=15
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to retrieve semantically matched jobs")
    except Exception as e:
        return None, f"Connection error: {str(e)}"


