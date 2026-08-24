import os
import sys
import uuid
import pytest

# Ensure workspace root and backend directory are in sys.path
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import api_client

def test_full_frontend_e2e_integration_flow():
    """Performs full end-to-end validation of all frontend integration steps:
    Auth, Profile, Preferences, Resume Upload, User Isolation, and Persistence."""

    # 1. Health check
    assert api_client.check_backend_health() is True, "FastAPI backend health check failed"

    # 2. Register & Login User A
    rand_a = uuid.uuid4().hex[:8]
    email_a = f"user_a_{rand_a}@example.com"
    pwd_a = "SecretPass123!"
    name_a = f"User A {rand_a}"

    reg_a, reg_err_a = api_client.register_user(name_a, email_a, pwd_a)
    assert reg_a is not None, f"User A registration failed: {reg_err_a}"

    token_a, login_err_a = api_client.login_user(email_a, pwd_a)
    assert token_a is not None, f"User A login failed: {login_err_a}"

    # Get User A details
    me_a, me_err_a = api_client.get_current_user(token_a)
    assert me_a is not None and me_a["email"] == email_a

    # 3. Update User A Profile
    profile_payload_a = {
        "target_role": "AI Engineer",
        "experience_level": "Fresher",
        "preferred_locations": ["India", "Remote"],
        "work_mode_preference": "Remote",
        "employment_type": "Full-time",
        "min_match_score": 80.0
    }
    updated_prof_a, prof_err_a = api_client.update_user_profile(token_a, profile_payload_a)
    assert updated_prof_a is not None, f"Profile update failed: {prof_err_a}"
    assert updated_prof_a["target_role"] == "AI Engineer"
    assert updated_prof_a["preferred_locations"] == ["India", "Remote"]
    assert updated_prof_a["min_match_score"] == 80.0

    # 4. Update User A Job Preferences
    prefs_payload_a = {
        "auto_apply_enabled": True,
        "daily_apply_limit": 5,
        "desired_job_titles": ["AI Engineer", "GenAI Engineer", "ML Engineer"],
        "preferred_industries": ["AI", "Software"],
        "min_salary": 500000.0
    }
    updated_prefs_a, prefs_err_a = api_client.update_user_preferences(token_a, prefs_payload_a)
    assert updated_prefs_a is not None, f"Preferences update failed: {prefs_err_a}"
    assert updated_prefs_a["auto_apply_enabled"] is True
    assert updated_prefs_a["daily_apply_limit"] == 5
    assert updated_prefs_a["desired_job_titles"] == ["AI Engineer", "GenAI Engineer", "ML Engineer"]
    assert updated_prefs_a["min_salary"] == 500000.0

    # 5. Upload Resume for User A
    valid_docx_path = os.path.join(WORKSPACE_DIR, "backend", "uploads", "resumes", "1_ecf1fbe0_jane_resume.docx")
    with open(valid_docx_path, "rb") as f:
        test_docx_content = f.read()

    res_a, res_err_a = api_client.upload_resume(token_a, test_docx_content, "user_a_resume.docx")
    assert res_a is not None, f"Resume upload failed: {res_err_a}"
    resume_id_a = res_a["id"]


    resumes_list_a, list_err_a = api_client.get_user_resumes(token_a)
    assert resumes_list_a is not None and len(resumes_list_a) >= 1
    assert any(r["id"] == resume_id_a for r in resumes_list_a)

    # 5.5 Fetch Jobs via FastAPI Jobs API
    jobs_a, jobs_err_a = api_client.get_jobs(token_a, search="Python", limit=10)
    assert jobs_a is not None, f"Jobs API call failed: {jobs_err_a}"
    assert "jobs" in jobs_a and "total" in jobs_a

    # 6. User B Registration & Login (User Isolation Check)
    rand_b = uuid.uuid4().hex[:8]
    email_b = f"user_b_{rand_b}@example.com"
    pwd_b = "SecretPass123!"
    name_b = f"User B {rand_b}"

    reg_b, _ = api_client.register_user(name_b, email_b, pwd_b)
    token_b, _ = api_client.login_user(email_b, pwd_b)
    assert token_b is not None

    # Fetch User B profile & preferences
    prof_b, _ = api_client.get_user_profile(token_b)
    prefs_b, _ = api_client.get_user_preferences(token_b)
    resumes_b, _ = api_client.get_user_resumes(token_b)

    # Verify User Isolation: User B MUST NOT see User A's data
    assert prof_b["target_role"] != "AI Engineer"
    assert prefs_b["auto_apply_enabled"] is False
    assert prefs_b["daily_apply_limit"] == 10
    assert len(resumes_b) == 0

    # Update User B Profile
    api_client.update_user_profile(token_b, {"target_role": "Backend Developer", "experience_level": "Senior"})

    # 7. Relogin User A & Verify Persistence
    re_token_a, _ = api_client.login_user(email_a, pwd_a)
    re_prof_a, _ = api_client.get_user_profile(re_token_a)
    re_prefs_a, _ = api_client.get_user_preferences(re_token_a)
    re_resumes_a, _ = api_client.get_user_resumes(re_token_a)

    assert re_prof_a["target_role"] == "AI Engineer"
    assert re_prof_a["experience_level"] == "Fresher"
    assert re_prefs_a["auto_apply_enabled"] is True
    assert re_prefs_a["daily_apply_limit"] == 5
    assert len(re_resumes_a) >= 1
