import os
import sys
import uuid
import pytest

# Ensure backend directory is at the top of sys.path before root app.py
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_random_user():
    """Helper function to register and log in a unique user, returning user data & auth headers."""
    random_str = uuid.uuid4().hex[:8]
    email = f"user_{random_str}@example.com"
    password = "SecretPassword123!"
    name = f"Test User {random_str}"

    # Register
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "name": name
    })
    assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.text}"

    # Login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    return {"email": email, "headers": headers, "token": token}

def test_health_endpoints():
    """Verify system health endpoints."""
    r1 = client.get("/health")
    assert r1.status_code == 200
    assert r1.json() == {"status": "ok"}

    r2 = client.get("/api/v1/health")
    assert r2.status_code == 200
    assert r2.json() == {"status": "ok"}

def test_unauthenticated_access():
    """Verify profile & preferences endpoints require authentication."""
    r_prof = client.get("/api/v1/profile")
    assert r_prof.status_code == 401

    r_pref = client.get("/api/v1/preferences")
    assert r_pref.status_code == 401

def test_profile_crud_and_user_isolation():
    """Verify profile CRUD and strict data isolation between User A and User B."""
    user_a = create_random_user()
    user_b = create_random_user()

    # 1. User A retrieves initial profile
    get_a_initial = client.get("/api/v1/profile", headers=user_a["headers"])
    assert get_a_initial.status_code == 200
    profile_a = get_a_initial.json()
    assert profile_a["target_role"] is None

    # 2. User A updates profile
    update_payload_a = {
        "target_role": "Senior AI Engineer",
        "experience_level": "Senior",
        "preferred_locations": ["Remote", "San Francisco, CA"],
        "work_mode_preference": "Remote",
        "employment_type": "Full-time",
        "min_match_score": 85.0
    }
    put_a = client.put("/api/v1/profile", json=update_payload_a, headers=user_a["headers"])
    assert put_a.status_code == 200
    data_a = put_a.json()
    assert data_a["target_role"] == "Senior AI Engineer"
    assert data_a["preferred_locations"] == ["Remote", "San Francisco, CA"]
    assert data_a["min_match_score"] == 85.0

    # 3. User B retrieves profile -> should NOT see User A's profile
    get_b = client.get("/api/v1/profile", headers=user_b["headers"])
    assert get_b.status_code == 200
    data_b = get_b.json()
    assert data_b["target_role"] is None
    assert data_b["user_id"] != data_a["user_id"]

    # 4. User B updates profile independently
    update_payload_b = {
        "target_role": "Junior Data Analyst",
        "experience_level": "Entry"
    }
    put_b = client.put("/api/v1/profile", json=update_payload_b, headers=user_b["headers"])
    assert put_b.status_code == 200
    assert put_b.json()["target_role"] == "Junior Data Analyst"

    # 5. User A retrieves profile again -> remains unchanged
    get_a_final = client.get("/api/v1/profile", headers=user_a["headers"])
    assert get_a_final.status_code == 200
    assert get_a_final.json()["target_role"] == "Senior AI Engineer"

def test_preferences_crud_and_user_isolation():
    """Verify job preferences CRUD and strict data isolation between User A and User B."""
    user_a = create_random_user()
    user_b = create_random_user()

    # 1. User A retrieves initial preferences
    get_a_initial = client.get("/api/v1/preferences", headers=user_a["headers"])
    assert get_a_initial.status_code == 200
    prefs_a = get_a_initial.json()
    assert prefs_a["auto_apply_enabled"] is False
    assert prefs_a["daily_apply_limit"] == 10

    # 2. User A updates preferences
    update_payload_a = {
        "auto_apply_enabled": True,
        "daily_apply_limit": 25,
        "desired_job_titles": ["AI Engineer", "ML Ops Engineer"],
        "preferred_industries": ["Technology", "AI & Robotics"],
        "min_salary": 150000.0
    }
    put_a = client.put("/api/v1/preferences", json=update_payload_a, headers=user_a["headers"])
    assert put_a.status_code == 200
    data_a = put_a.json()
    assert data_a["auto_apply_enabled"] is True
    assert data_a["daily_apply_limit"] == 25
    assert data_a["desired_job_titles"] == ["AI Engineer", "ML Ops Engineer"]

    # 3. User B retrieves preferences -> should see User B's defaults
    get_b = client.get("/api/v1/preferences", headers=user_b["headers"])
    assert get_b.status_code == 200
    data_b = get_b.json()
    assert data_b["auto_apply_enabled"] is False
    assert data_b["daily_apply_limit"] == 10
    assert data_b["user_id"] != data_a["user_id"]

def test_existing_resumes_and_auth_integrity():
    """Verify existing auth and resume endpoints remain fully functional."""
    user = create_random_user()
    
    # Check /auth/me
    me_resp = client.get("/api/v1/auth/me", headers=user["headers"])
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == user["email"]

    # Check /resumes list
    resumes_resp = client.get("/api/v1/resumes", headers=user["headers"])
    assert resumes_resp.status_code == 200
    assert isinstance(resumes_resp.json(), list)
