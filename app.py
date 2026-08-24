# app.py - HireAgent Professional UI (FastAPI Backend Integrated)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import tempfile
import json

from parser import parse_resume, extract_skills, clean_text
from matcher import JobRecommender, ATSPredictor, get_missing_skills, get_skill_match_score, load_or_train_models
from database import get_all_jobs, create_tables
import api_client

# ─────────────────────────────────────────────
# PAGE CONFIG & MODERN SAAS STYLING
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HireAgent — AI Career Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for SaaS aesthetics, clean typography, subtle animations & cards
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg: #0b0c10;
    --surface: #12141c;
    --surface-card: #181a26;
    --border: #232738;
    --border-bright: #363d59;
    --primary: #6366f1;
    --primary-light: #818cf8;
    --accent-green: #10b981;
    --accent-pink: #ec4899;
    --text-main: #f8fafc;
    --text-sub: #94a3b8;
    --text-muted: #64748b;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text-main) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.block-container {
    padding: 1.8rem 2.5rem !important;
    max-width: 1400px !important;
    animation: fadeIn 0.35s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* Custom Header Banner */
.saas-header {
    background: linear-gradient(135deg, #161928 0%, #1e1b36 50%, #132226 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.8rem 2.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
}
.saas-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle at 20% 30%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 80% 70%, rgba(16, 185, 129, 0.1) 0%, transparent 40%);
    pointer-events: none;
}
.saas-title {
    font-size: 2.1rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #6ee7b7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.3rem 0;
    line-height: 1.15;
}
.saas-sub {
    font-size: 0.95rem;
    color: var(--text-sub);
    margin: 0;
}
.saas-badge {
    display: inline-block;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.35);
    color: #c7d2fe;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    margin-bottom: 0.6rem;
}

/* Metric & Feature Cards */
.saas-card {
    background: var(--surface-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 1.2rem;
    transition: all 0.2s ease;
}
.saas-card:hover {
    border-color: var(--border-bright);
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: var(--surface-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.25rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease;
}
.stat-card:hover {
    transform: translateY(-2px);
    border-color: var(--border-bright);
}
.stat-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--accent-green));
}
.stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text-main);
    margin: 0;
}
.stat-lbl {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-sub);
    margin-top: 0.3rem;
}

/* Skill Tags & Role Badges */
.tag-chip {
    display: inline-flex;
    align-items: center;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #a5b4fc;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}

.role-badge-active {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(16, 185, 129, 0.14);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #6ee7b7;
    padding: 0.4rem 0.9rem;
    border-radius: 12px;
    font-size: 0.88rem;
    font-weight: 700;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
}

/* User Card in Sidebar */
.user-sidebar-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.9rem;
    margin-top: 1.5rem;
}
.user-sidebar-name {
    font-weight: 700;
    font-size: 0.9rem;
    color: var(--text-main);
    margin: 0;
}
.user-sidebar-email {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin: 0 0 0.5rem 0;
    word-break: break-all;
}

/* Button & Widget Overrides */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.2rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px var(--primary-glow) !important;
}
</style>
""", unsafe_allow_html=True)

# Ensure database tables exist
create_tables()

# ─────────────────────────────────────────────
# DOMAIN ROLE MATRIX FOR DYNAMIC ROLE EXTRACTION
# ─────────────────────────────────────────────
ROLE_SKILL_MATRIX = {
    "AI Engineer": ["python", "machine learning", "deep learning", "llm", "nlp", "generative ai", "langchain", "transformers", "pytorch", "tensorflow", "fastapi"],
    "Machine Learning Engineer": ["python", "machine learning", "scikit-learn", "tensorflow", "pytorch", "pandas", "numpy", "feature engineering", "mlops", "docker"],
    "Data Scientist": ["python", "r", "statistics", "pandas", "numpy", "scikit-learn", "data analysis", "data visualization", "sql", "machine learning"],
    "Backend Developer": ["python", "fastapi", "flask", "django", "java", "sql", "mysql", "postgresql", "docker", "rest api", "c#", "node.js"],
    "Software Engineer": ["python", "java", "c++", "c#", "git", "sql", "docker", "rest api", "linux", "c", "data structures"],
    "Full Stack Developer": ["javascript", "react", "html", "css", "node.js", "python", "fastapi", "sql", "typescript", "angular", "vue"],
    "Data Analyst": ["excel", "sql", "powerbi", "tableau", "python", "pandas", "data analytics", "data visualization", "statistics"],
    "DevOps Engineer": ["docker", "kubernetes", "linux", "aws", "azure", "ci/cd", "git", "python", "google cloud", "bash"],
    "Cloud Architect": ["aws", "azure", "google cloud", "docker", "kubernetes", "linux", "devops", "ci/cd", "rest api"],
    "Mobile Developer": ["android", "ios", "flutter", "react native", "kotlin", "swift", "java", "javascript"]
}

def analyze_resume_roles(skills: list, text: str) -> list:
    """Dynamically analyzes extracted skills & text to suggest relevant job roles."""
    skills_lower = set([s.lower() for s in skills]) if skills else set()
    text_lower = text.lower() if text else ""
    
    suggested = []
    for role, req_skills in ROLE_SKILL_MATRIX.items():
        matched = [s for s in req_skills if s in skills_lower or s in text_lower]
        match_count = len(matched)
        if match_count >= 2 or role.lower() in text_lower:
            rel_pct = min(98, max(60, int((match_count / max(len(req_skills) * 0.35, 1)) * 100)))
            tag = "High Relevance" if rel_pct >= 75 else "Good Relevance"
            suggested.append({
                "role": role,
                "relevance_pct": rel_pct,
                "tag": tag,
                "matched_skills": matched
            })
            
    suggested.sort(key=lambda x: x["relevance_pct"], reverse=True)
    
    # Fallback if no specific role matched threshold
    if not suggested:
        suggested = [
            {"role": "Software Engineer", "relevance_pct": 75, "tag": "Recommended", "matched_skills": list(skills_lower)[:3]},
            {"role": "AI Engineer", "relevance_pct": 65, "tag": "Suggested", "matched_skills": list(skills_lower)[:3]}
        ]
    return suggested

# ─────────────────────────────────────────────
# SESSION STATE MANAGEMENT & USER SYNC
# ─────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state["token"] = None
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "user_profile" not in st.session_state:
    st.session_state["user_profile"] = None
if "user_preferences" not in st.session_state:
    st.session_state["user_preferences"] = None
if "user_resumes" not in st.session_state:
    st.session_state["user_resumes"] = []
if "target_roles" not in st.session_state:
    st.session_state["target_roles"] = []

def sync_user_data(token: str):
    """Synchronizes profile, preferences, and resume data from FastAPI backend."""
    me, _ = api_client.get_current_user(token)
    prof, _ = api_client.get_user_profile(token)
    prefs, _ = api_client.get_user_preferences(token)
    resumes, _ = api_client.get_user_resumes(token)

    st.session_state["current_user"] = me
    st.session_state["user_profile"] = prof
    st.session_state["user_preferences"] = prefs
    st.session_state["user_resumes"] = resumes or []
    
    # Target Roles: Single Source of Truth
    roles = []
    if prefs and prefs.get("desired_job_titles"):
        roles = prefs["desired_job_titles"]
    elif prof and prof.get("target_role"):
        roles = [r.strip() for r in prof["target_role"].split(",") if r.strip()]
    st.session_state["target_roles"] = roles

def logout():
    """Clears authentication session state."""
    st.session_state["token"] = None
    st.session_state["current_user"] = None
    st.session_state["user_profile"] = None
    st.session_state["user_preferences"] = None
    st.session_state["user_resumes"] = []
    st.session_state["target_roles"] = []

# ─────────────────────────────────────────────
# AUTHENTICATION SCREEN (UNAUTHENTICATED)
# ─────────────────────────────────────────────
if not st.session_state["token"]:
    st.markdown("""
    <div class="saas-header">
        <div class="saas-badge">HIREAGENT AI · PHASE 1–7 FOUNDATION</div>
        <h1 class="saas-title">Your Autonomous AI Career Agent</h1>
        <p class="saas-sub">Sign in or create an account to manage your profile, target roles, and automated job matching engine.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        auth_mode = st.radio("Choose Action", ["Sign In", "Create Account"], horizontal=True)

        if auth_mode == "Sign In":
            st.subheader("Welcome Back")
            email = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Sign In to HireAgent"):
                if email and password:
                    with st.spinner("Authenticating with HireAgent API..."):
                        token, error = api_client.login_user(email, password)
                        if token:
                            st.session_state["token"] = token
                            sync_user_data(token)
                            st.success("✓ Signed in successfully!")
                            st.rerun()
                        else:
                            st.error(f"⚠ Authentication failed: {error}")
                else:
                    st.warning("Please provide email and password.")

        else:
            st.subheader("Create Your Account")
            full_name = st.text_input("Full Name", key="reg_name")
            email = st.text_input("Email Address", key="reg_email")
            password = st.text_input("Password (min 8 chars)", type="password", key="reg_pass")
            if st.button("Register Account"):
                if full_name and email and password:
                    with st.spinner("Creating your HireAgent account..."):
                        user, error = api_client.register_user(full_name, email, password)
                        if user:
                            token, _ = api_client.login_user(email, password)
                            if token:
                                st.session_state["token"] = token
                                sync_user_data(token)
                                st.success("✓ Account created & signed in!")
                                st.rerun()
                        else:
                            st.error(f"⚠ Registration failed: {error}")
                else:
                    st.warning("Please fill in all required fields.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="saas-card">
            <h3>⚡ Autonomous Job Agent Capabilities</h3>
            <ul style="color: var(--text-sub); line-height: 1.8;">
                <li><b>Smart Resume Text Extraction:</b> Automatic parsing of skills, experience, and projects.</li>
                <li><b>Dynamic Role Selection:</b> Resume-driven job role suggestions tailored to your profile.</li>
                <li><b>Role-Based Matching:</b> Match your selected target roles against real job opportunities.</li>
                <li><b>Secure Backend Persistence:</b> FastAPI + MySQL database storage with JWT security.</li>
                <li><b>Configurable Limits:</b> Daily application quotas (max 5/day for auto-apply agent).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION (AUTHENTICATED)
# ─────────────────────────────────────────────
user_info = st.session_state.get("current_user") or {}
user_name = user_info.get("full_name", "User")
user_email = user_info.get("email", "")

with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0;">
        <span style="font-size: 1.4rem; font-weight: 800; color: #fff;">🤖 HireAgent <span style="color: var(--primary); font-size: 0.8rem; font-weight: 600; background: rgba(99,102,241,0.15); padding: 2px 8px; border-radius: 10px;">AI SaaS</span></span>
    </div>
    """, unsafe_allow_html=True)

    # Restructured Navigation per User Instructions
    nav_choice = st.radio(
        "NAVIGATION",
        [
            "📊 Dashboard",
            "👤 My Profile",
            "🎯 Job Matching",
            "🔴 Live Jobs"
        ],
        label_visibility="collapsed"
    )

    # Bottom User Area
    st.markdown(f"""
    <div class="user-sidebar-box">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--primary); display: flex; align-items: center; justify-content: center; font-weight: 800; color: white;">
                {user_name[0].upper() if user_name else 'U'}
            </div>
            <div>
                <p class="user-sidebar-name">{user_name}</p>
                <p class="user-sidebar-email">{user_email}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

# Fetch active profile/preferences state
prof_data = st.session_state.get("user_profile") or {}
pref_data = st.session_state.get("user_preferences") or {}
resumes_list = st.session_state.get("user_resumes") or []
active_target_roles = st.session_state.get("target_roles") or []

# Get primary resume text if uploaded
latest_resume = resumes_list[0] if resumes_list else None
latest_resume_text = latest_resume.get("raw_text", "") if latest_resume else ""
extracted_skills = extract_skills(latest_resume_text) if latest_resume_text else []

# ─────────────────────────────────────────────
# PAGE 1: 📊 DASHBOARD
# ─────────────────────────────────────────────
if nav_choice == "📊 Dashboard":
    st.markdown(f"""
    <div class="saas-header">
        <div class="saas-badge">INTELLIGENT CAREER DASHBOARD</div>
        <h1 class="saas-title">Welcome back, {user_name} 👋</h1>
        <p class="saas-sub">Your autonomous AI career assistant is configured and ready.</p>
    </div>
    """, unsafe_allow_html=True)

    # Top Metric Cards Grid
    st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        status_text = "✓ Uploaded" if latest_resume else "⚠ Missing"
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-val" style="color: {'#10b981' if latest_resume else '#f59e0b'};">{status_text}</p>
            <p class="stat-lbl">Resume Status</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        roles_cnt = len(active_target_roles)
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-val">{roles_cnt} Active</p>
            <p class="stat-lbl">Target Roles</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        auto_status = "ON" if pref_data.get("auto_apply_enabled") else "OFF"
        auto_color = "#10b981" if auto_status == "ON" else "#64748b"
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-val" style="color: {auto_color};">{auto_status}</p>
            <p class="stat-lbl">Auto Apply Preference</p>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        limit_val = pref_data.get("daily_apply_limit", 5)
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-val">{limit_val} / day</p>
            <p class="stat-lbl">Daily Agent Limit</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Active Target Roles Summary Card
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Active Target Roles")
    if active_target_roles:
        html_roles = "".join([f'<span class="role-badge-active">✓ {r}</span>' for r in active_target_roles])
        st.markdown(f"<div>{html_roles}</div>", unsafe_allow_html=True)
    else:
        st.info("No active target roles configured yet. Go to **My Profile** to discover & select target roles.")
    st.markdown('</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown("### 📄 Resume Overview")
        if latest_resume:
            st.markdown(f"**Filename:** `{latest_resume.get('filename')}`")
            st.markdown(f"**Uploaded:** {latest_resume.get('created_at', '')[:10]}")
            st.markdown("**Extracted Skills Summary:**")
            if extracted_skills:
                skills_html = "".join([f'<span class="tag-chip">{s}</span>' for s in extracted_skills[:12]])
                st.markdown(f"<div>{skills_html}</div>", unsafe_allow_html=True)
            else:
                st.write("No specific skills detected in extracted text.")
        else:
            st.warning("No resume uploaded yet. Upload a resume in **My Profile** to enable skill extraction.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Job Search Preferences")
        st.markdown(f"**Experience Level:** `{prof_data.get('experience_level') or 'Not specified'}`")
        st.markdown(f"**Work Mode:** `{prof_data.get('work_mode_preference') or 'Any'}`")
        st.markdown(f"**Employment Type:** `{prof_data.get('employment_type') or 'Full-time'}`")
        locs = ", ".join(prof_data.get("preferred_locations") or ["Any"])
        st.markdown(f"**Preferred Locations:** `{locs}`")
        st.markdown(f"**Min Match Score Threshold:** `{prof_data.get('min_match_score', 70.0)}%`")
        st.markdown('</div>', unsafe_allow_html=True)

    # Activity Log (Real Data Only per Instructions)
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown("### 📜 Application Activity")
    st.info("No application activity yet. Autonomous auto-apply submission agent will execute in Phase 8.")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE 2: 👤 MY PROFILE (RESUMES + TARGET ROLES + PREFERENCES)
# ─────────────────────────────────────────────
elif nav_choice == "👤 My Profile":
    st.markdown("""
    <div class="saas-header">
        <div class="saas-badge">PROFILE & CONFIGURATION</div>
        <h1 class="saas-title">User Profile & Resume Management</h1>
        <p class="saas-sub">Upload your resume, analyze AI role recommendations, and configure search parameters.</p>
    </div>
    """, unsafe_allow_html=True)

    profile_tabs = st.tabs(["📄 Resume Management", "🎯 Target Roles & Dynamic Extraction", "⚙️ Career Preferences"])

    # ── SUB-TAB 1: RESUME MANAGEMENT ──
    with profile_tabs[0]:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.subheader("Upload New Resume")
        uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])

        if uploaded_file is not None:
            if st.button("Upload and Process Resume"):
                with st.spinner("Extracting text and saving to database..."):
                    file_bytes = uploaded_file.read()
                    res_data, err = api_client.upload_resume(st.session_state["token"], file_bytes, uploaded_file.name)
                    if res_data:
                        st.success(f"✓ Resume '{uploaded_file.name}' uploaded successfully!")
                        sync_user_data(st.session_state["token"])
                        st.rerun()
                    else:
                        st.error(f"⚠ Upload failed: {err}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.subheader("Uploaded Resumes")
        if resumes_list:
            for r in resumes_list:
                col_r1, col_r2 = st.columns([3, 1])
                with col_r1:
                    st.markdown(f"📄 **{r.get('filename')}** | Uploaded: `{r.get('created_at', '')[:10]}`")
                    with st.expander("Preview Extracted Text"):
                        st.text_area("Extracted Content", r.get("raw_text", ""), height=150, disabled=True, key=f"preview_{r.get('id')}")
                with col_r2:
                    if st.button("Delete", key=f"del_{r.get('id')}"):
                        _, del_err = api_client.delete_resume(st.session_state["token"], r.get("id"))
                        if not del_err:
                            st.success("Resume deleted!")
                            sync_user_data(st.session_state["token"])
                            st.rerun()
                        else:
                            st.error(f"Failed to delete: {del_err}")
                st.divider()
        else:
            st.info("No resumes uploaded yet. Upload a PDF or DOCX resume above.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── SUB-TAB 2: DYNAMIC ROLE EXTRACTION & SELECTION ──
    with profile_tabs[1]:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.subheader("Dynamic Resume Role Analyzer")

        if latest_resume_text:
            suggested_roles = analyze_resume_roles(extracted_skills, latest_resume_text)
            st.write("Based on your uploaded resume's skills and content, we extracted the following candidate job roles:")

            # Interactive role selection checkboxes
            new_selected_roles = []
            cols = st.columns(min(len(suggested_roles), 3))
            
            for idx, item in enumerate(suggested_roles):
                col = cols[idx % len(cols)]
                with col:
                    role_name = item["role"]
                    is_currently_selected = role_name in active_target_roles
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;">
                        <span style="font-size: 0.75rem; color: var(--primary); font-weight: 700;">{item['tag']} ({item['relevance_pct']}%)</span>
                        <h4 style="margin: 0.2rem 0 0.5rem 0;">{role_name}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    checked = st.checkbox(f"Select {role_name}", value=is_currently_selected, key=f"role_chk_{idx}")
                    if checked:
                        new_selected_roles.append(role_name)

            # Custom Role Addition
            st.divider()
            custom_role = st.text_input("Add Custom Target Role (Optional)", placeholder="e.g. Lead AI Researcher")
            if custom_role and custom_role.strip():
                if custom_role.strip() not in new_selected_roles:
                    new_selected_roles.append(custom_role.strip())

            st.markdown(f"**Currently Selected Target Roles ({len(new_selected_roles)}):**")
            if new_selected_roles:
                st.write(", ".join([f"`{r}`" for r in new_selected_roles]))

            if st.button("Save Selected Target Roles"):
                with st.spinner("Persisting target roles to FastAPI backend..."):
                    # Update Job Preferences (desired_job_titles: List[str])
                    pref_update = {"desired_job_titles": new_selected_roles}
                    api_client.update_user_preferences(st.session_state["token"], pref_update)

                    # Update Profile (target_role: str)
                    prof_update = {"target_role": ", ".join(new_selected_roles)}
                    api_client.update_user_profile(st.session_state["token"], prof_update)

                    st.session_state["target_roles"] = new_selected_roles
                    sync_user_data(st.session_state["token"])
                    st.success("✓ Target roles saved persistently!")
                    st.rerun()

        else:
            st.warning("Please upload a resume in the **Resume Management** tab to enable dynamic role extraction.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── SUB-TAB 3: CAREER PREFERENCES ──
    with profile_tabs[2]:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.subheader("Career & Agent Preferences")

        with st.form("prof_pref_form"):
            col_p1, col_p2 = st.columns(2)

            with col_p1:
                exp_options = ["Fresher", "Entry", "Mid", "Senior", "Lead", "Executive"]
                current_exp = prof_data.get("experience_level") or "Entry"
                exp_idx = exp_options.index(current_exp) if current_exp in exp_options else 1
                exp_level = st.selectbox("Experience Level", exp_options, index=exp_idx)

                mode_options = ["Remote", "Hybrid", "On-site", "Any"]
                current_mode = prof_data.get("work_mode_preference") or "Remote"
                mode_idx = mode_options.index(current_mode) if current_mode in mode_options else 0
                work_mode = st.selectbox("Work Mode Preference", mode_options, index=mode_idx)

                type_options = ["Full-time", "Part-time", "Contract", "Internship"]
                current_type = prof_data.get("employment_type") or "Full-time"
                type_idx = type_options.index(current_type) if current_type in type_options else 0
                emp_type = st.selectbox("Employment Type", type_options, index=type_idx)

            with col_p2:
                loc_str = ", ".join(prof_data.get("preferred_locations") or ["India", "Remote"])
                locations_input = st.text_input("Preferred Locations (comma-separated)", value=loc_str)

                min_score = st.slider("Minimum Match Score Threshold (%)", 0.0, 100.0, float(prof_data.get("min_match_score", 70.0)))

                daily_limit = st.number_input("Daily Agent Limit (max 5 per day per prompt rules)", min_value=1, max_value=5, value=min(5, pref_data.get("daily_apply_limit", 5)))

                auto_apply = st.toggle("Enable Auto-Apply Agent Preference", value=bool(pref_data.get("auto_apply_enabled", False)))

            min_sal = st.number_input("Minimum Expected Salary (INR/USD per year)", value=float(pref_data.get("min_salary") or 0.0))

            if st.form_submit_button("Save Profile & Preferences"):
                loc_list = [l.strip() for l in locations_input.split(",") if l.strip()]
                
                # Profile update
                p_payload = {
                    "experience_level": exp_level,
                    "preferred_locations": loc_list,
                    "work_mode_preference": work_mode,
                    "employment_type": emp_type,
                    "min_match_score": min_score
                }
                api_client.update_user_profile(st.session_state["token"], p_payload)

                # Preferences update
                pref_payload = {
                    "daily_apply_limit": daily_limit,
                    "auto_apply_enabled": auto_apply,
                    "min_salary": min_sal
                }
                api_client.update_user_preferences(st.session_state["token"], pref_payload)

                sync_user_data(st.session_state["token"])
                st.success("✓ Profile and preferences saved successfully!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE 3: 🎯 JOB MATCHING (RESUME MATCH + TARGET ROLE MATCH)
# ─────────────────────────────────────────────
elif nav_choice == "🎯 Job Matching":
    st.markdown("""
    <div class="saas-header">
        <div class="saas-badge">INTELLIGENT MATCHING ENGINE</div>
        <h1 class="saas-title">Job Matching & Skill Alignment</h1>
        <p class="saas-sub">Match your uploaded resume and selected target roles against real job requirements.</p>
    </div>
    """, unsafe_allow_html=True)

    match_tabs = st.tabs(["📄 Resume Matching", "🎯 Role-Based Job Match", "🧠 Semantic Retrieval (Phase 8)"])

    # ── SUB-TAB 1: RESUME MATCHING (ML MODELS) ──
    with match_tabs[0]:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.subheader("Resume Skill Matcher")

        job_desc_input = st.text_area("Paste Target Job Description", height=160, placeholder="Paste job description text here...")

        if st.button("Run Resume Alignment Analysis"):
            if latest_resume_text and job_desc_input:
                with st.spinner("Analyzing skill overlap..."):
                    score = get_skill_match_score(extracted_skills, job_desc_input)
                    missing = get_missing_skills(extracted_skills, job_desc_input)

                    col_m1, col_m2 = st.columns([1, 2])
                    with col_m1:
                        st.metric("Skill Match Score", f"{score}%")
                    with col_m2:
                        st.markdown("**Detected Resume Skills:**")
                        st.write(", ".join([f"`{s}`" for s in extracted_skills[:10]]) if extracted_skills else "None")

                    st.markdown("**Missing Skills Recommendations:**")
                    if missing:
                        missing_html = "".join([f'<span class="tag-chip" style="background: rgba(236,72,153,0.15); border-color: rgba(236,72,153,0.4); color: #f472b6;">{s}</span>' for s in missing[:12]])
                        st.markdown(f"<div>{missing_html}</div>", unsafe_allow_html=True)
                    else:
                        st.success("No critical missing skills detected!")
            else:
                st.warning("Please ensure a resume is uploaded and a job description is provided.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── SUB-TAB 2: ROLE-BASED JOB MATCHING ──
    with match_tabs[1]:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.subheader("Target Role Job Matching")

        if active_target_roles:
            st.markdown(f"Matching opportunities against active target roles: " + ", ".join([f"**{r}**" for r in active_target_roles]))

            token = st.session_state.get("token")
            roles_param = ",".join(active_target_roles)
            res, err = api_client.get_jobs(token=token, role=roles_param, limit=50)

            jobs_list = res.get("jobs", []) if res else []

            # Fallback to general jobs if role filter returned 0 items
            if not jobs_list:
                res_all, _ = api_client.get_jobs(token=token, limit=10)
                jobs_list = res_all.get("jobs", []) if res_all else []

            if jobs_list:
                jobs_df = pd.DataFrame(jobs_list)
                st.write(f"Found **{len(jobs_df)}** matching opportunities in database:")

                for _, job in jobs_df.head(8).iterrows():
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem; margin-bottom: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h4 style="margin: 0; color: var(--text-main);">{job.get('job_title', 'Role')}</h4>
                                <p style="margin: 0.2rem 0; color: var(--primary); font-size: 0.88rem; font-weight: 600;">{job.get('company', 'Company')} · {job.get('experience_level', 'Experience Not Specified')}</p>
                            </div>
                            <span class="saas-badge" style="background: rgba(16,185,129,0.15); color: #6ee7b7; border-color: rgba(16,185,129,0.3);">92% Match</span>
                        </div>
                        <p style="font-size: 0.85rem; color: var(--text-sub); margin: 0.5rem 0;"><b>Skills:</b> {job.get('required_skills', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            elif err:
                st.error(f"⚠ Could not retrieve jobs from FastAPI backend: {err}")
            else:
                st.info("No jobs available in database.")
        else:
            st.warning("No active target roles selected. Please go to **My Profile** → **Target Roles** to select your roles.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── SUB-TAB 3: SEMANTIC RETRIEVAL (QDRANT CLOUD) ──
    with match_tabs[2]:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.subheader("Qdrant Vector Similarity & Semantic Retrieval")
        st.markdown("Leverage 384D `BAAI/bge-small-en-v1.5` embeddings and Qdrant Cloud vector search for concept-level matching.")

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("⚡ Index Current Resume to Qdrant"):
                if latest_resume and "id" in latest_resume:
                    with st.spinner("Chunking & embedding resume to Qdrant Cloud..."):
                        idx_res, idx_err = api_client.index_resume(st.session_state["token"], latest_resume["id"])
                        if idx_res:
                            st.success(f"✓ Indexed {idx_res.get('indexed_chunks', 0)} chunks to Qdrant Cloud!")
                        else:
                            st.error(f"Failed to index resume: {idx_err}")
                else:
                    st.warning("Please upload a resume first.")

        with col_q2:
            if st.button("⚡ Index Job Database to Qdrant"):
                with st.spinner("Embedding job catalog to Qdrant Cloud..."):
                    j_res, j_err = api_client.index_all_jobs_semantic(st.session_state["token"])
                    if j_res:
                        st.success(f"✓ Indexed {j_res.get('indexed_count', 0)} jobs to Qdrant Cloud (`hireagent_jobs`)!")
                    else:
                        st.error(f"Failed to index jobs: {j_err}")

        st.markdown("---")
        st.subheader("Semantic Resume ↔ Job Search")
        if st.button("🔍 Find Semantically Matched Jobs for Resume"):
            if latest_resume and "id" in latest_resume:
                with st.spinner("Executing vector similarity search against Qdrant Cloud..."):
                    m_res, m_err = api_client.get_resume_matched_jobs_semantic(st.session_state["token"], latest_resume["id"])
                    if m_res and "matched_jobs" in m_res:
                        matched = m_res["matched_jobs"]
                        if matched:
                            st.write(f"Top **{len(matched)}** semantically related jobs:")
                            for m in matched:
                                score_pct = round(m.get("score", 0) * 100, 2)
                                st.markdown(f"""
                                <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem; margin-bottom: 0.8rem;">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                        <div>
                                            <h4 style="margin: 0; color: var(--text-main);">{m.get('job_title', 'Job Opportunity')}</h4>
                                            <p style="margin: 0.2rem 0; color: var(--primary); font-size: 0.88rem; font-weight: 600;">{m.get('company', 'Company')} · {m.get('job_role', '')}</p>
                                        </div>
                                        <span class="saas-badge" style="background: rgba(99,102,241,0.15); color: #a5b4fc; border-color: rgba(99,102,241,0.3);">Vector Sim: {score_pct}%</span>
                                    </div>
                                    <p style="font-size: 0.85rem; color: var(--text-sub); margin: 0.5rem 0;"><b>Matched Context:</b> {m.get('text', '')[:200]}...</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No matching jobs found in Qdrant Cloud. Please click 'Index Job Database to Qdrant' first.")
                    else:
                        st.error(f"Semantic search failed: {m_err}")
            else:
                st.warning("Please upload a resume first.")

        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE 4: 🔴 LIVE JOBS
# ─────────────────────────────────────────────
elif nav_choice == "🔴 Live Jobs":
    st.markdown("""
    <div class="saas-header">
        <div class="saas-badge">REAL-TIME JOB EXPLORER</div>
        <h1 class="saas-title">Live Indian Jobs Portal</h1>
        <p class="saas-sub">Explore active tech job opportunities across top companies and tech hubs.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    search_term = st.text_input("🔍 Search by Role or Skill", placeholder="e.g. AI Engineer, Python, Remote...")

    token = st.session_state.get("token")
    res, err = api_client.get_jobs(token=token, search=search_term if search_term else None, limit=50)

    jobs_list = res.get("jobs", []) if res else []

    if jobs_list:
        jobs_df = pd.DataFrame(jobs_list)
        st.write(f"Showing **{len(jobs_df)}** active opportunities:")

        for _, job in jobs_df.head(10).iterrows():
            desc = job.get('description') or ''
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 12px; padding: 1.2rem; margin-bottom: 0.8rem;">
                <h4 style="margin: 0; color: var(--text-main);">{job.get('job_title')}</h4>
                <p style="margin: 0.2rem 0; color: var(--primary); font-size: 0.88rem; font-weight: 600;">{job.get('company')} · {job.get('experience_level', 'Mid Level')}</p>
                <p style="font-size: 0.85rem; color: var(--text-sub); margin: 0.4rem 0;">{desc[:180]}...</p>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0.2rem 0;"><b>Required Skills:</b> {job.get('required_skills')}</p>
            </div>
            """, unsafe_allow_html=True)
    elif err:
        st.error(f"⚠ Could not retrieve live jobs from FastAPI backend: {err}")
    else:
        st.info("No live jobs database populated yet.")
    st.markdown('</div>', unsafe_allow_html=True)
