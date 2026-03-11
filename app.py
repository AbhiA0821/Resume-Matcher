# app.py - AI Resume & Job Matcher (Professional UI)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import tempfile
import requests

from parser import parse_resume, extract_skills, clean_text
from matcher import JobRecommender, ATSPredictor, get_missing_skills, get_skill_match_score, load_or_train_models
from database import get_all_jobs, create_tables

st.set_page_config(
    page_title="ResumeAI — Smart Job Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
:root {
    --bg: #0a0a0f; --surface: #111118; --surface2: #1a1a24;
    --border: #2a2a3a; --accent: #6c63ff; --accent2: #ff6584;
    --accent3: #43e97b; --text: #e8e8f0; --muted: #6b6b80;
}
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
.hero {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1025 50%, #0f1a1a 100%);
    border: 1px solid var(--border); border-radius: 20px;
    padding: 2.5rem 3rem; margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle at 30% 40%, rgba(108,99,255,0.12) 0%, transparent 50%),
                radial-gradient(circle at 70% 60%, rgba(67,233,123,0.08) 0%, transparent 50%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(135deg, #fff 0%, #6c63ff 50%, #43e97b 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0; line-height: 1.1;
}
.hero-sub { font-size: 1rem; color: var(--muted); margin: 0; }
.hero-badge {
    display: inline-block;
    background: rgba(108,99,255,0.15); border: 1px solid rgba(108,99,255,0.3);
    color: #a89fff; padding: 0.3rem 0.8rem; border-radius: 20px;
    font-size: 0.75rem; font-family: 'Space Mono', monospace;
    margin-bottom: 1rem; letter-spacing: 0.05em;
}
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
.metric-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 1.5rem; position: relative; overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover { transform: translateY(-2px); border-color: var(--accent); }
.metric-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent3));
}
.metric-num { font-size: 2.2rem; font-weight: 800; color: var(--text); margin: 0; font-family: 'Space Mono', monospace; }
.metric-label { font-size: 0.8rem; color: var(--muted); margin: 0.3rem 0 0 0; text-transform: uppercase; letter-spacing: 0.08em; }
.metric-icon { font-size: 1.5rem; margin-bottom: 0.5rem; }
.section-header {
    font-size: 1.2rem; font-weight: 700; color: var(--text);
    margin: 2rem 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;
    border-left: 3px solid var(--accent); padding-left: 0.8rem;
}
.skill-tag {
    display: inline-block;
    background: rgba(108,99,255,0.12); border: 1px solid rgba(108,99,255,0.25);
    color: #a89fff; padding: 0.25rem 0.7rem; border-radius: 20px;
    font-size: 0.78rem; margin: 0.2rem; font-family: 'Space Mono', monospace;
}
.info-pill {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem 1.5rem; text-align: center;
}
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #9b59b6) !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    transition: opacity 0.2s, transform 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; }
.stTextInput input, .stTextArea textarea {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Load Models ──
@st.cache_resource(ttl=0)
def load_everything():
    create_tables()
    jobs_df = get_all_jobs()
    ats_predictor, recommender = load_or_train_models(jobs_df)
    return ats_predictor, recommender, jobs_df

ats_predictor, recommender, jobs_df = load_everything()
if not recommender.is_fitted and len(jobs_df) > 0:
    recommender.fit(jobs_df)
    recommender.save()

RAPIDAPI_KEY = "46500ed60emsh8655fe0596fa7eap148e34jsn4f2ca5f482e4"

# ── Helper: Render Job Cards ──
def render_live_job_cards(live_jobs):
    for job in live_jobs:
        title      = job.get("job_title", "N/A")
        company    = job.get("employer_name", "N/A")
        job_city   = job.get("job_city", "")
        location   = f"{job_city}, India" if job_city else "India"
        job_type   = job.get("job_employment_type", "Full Time")
        posted     = (job.get("job_posted_at_datetime_utc", "") or "")[:10]
        apply_link = job.get("job_apply_link", "#")
        desc       = (job.get("job_description", "") or "")[:200] + "..."
        sal_min    = job.get("job_min_salary")
        sal_max    = job.get("job_max_salary")
        salary     = f"Rs.{sal_min:,.0f} - Rs.{sal_max:,.0f}" if sal_min and sal_max else "Not disclosed"
        logo       = job.get("employer_logo", "")
        source     = job.get("job_publisher", "Portal")
        logo_html  = f'<img src="{logo}" style="width:45px;height:45px;border-radius:10px;background:#fff;padding:4px;object-fit:contain">' if logo else '<div style="width:45px;height:45px;background:#2a2a3a;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.3rem">🏢</div>'
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0f0f1a,#1a1a24);
                    border:1px solid #2a2a3a;border-radius:16px;padding:1.2rem;
                    margin-bottom:0.8rem;position:relative;overflow:hidden">
            <div style="position:absolute;top:0;left:0;width:4px;height:100%;
                        background:linear-gradient(180deg,#6c63ff,#43e97b)"></div>
            <div style="display:flex;gap:1rem;align-items:flex-start;margin-left:0.5rem">
                {logo_html}
                <div style="flex:1">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.4rem">
                        <div>
                            <div style="font-size:1rem;font-weight:700;color:#e8e8f0;font-family:'Syne',sans-serif">{title}</div>
                            <div style="color:#6c63ff;font-weight:600;font-size:0.85rem;margin-top:0.15rem">{company}</div>
                        </div>
                        <div style="display:flex;gap:0.4rem;flex-wrap:wrap">
                            <div style="background:#43e97b22;color:#43e97b;padding:0.2rem 0.6rem;border-radius:20px;font-size:0.7rem;font-weight:600;border:1px solid #43e97b44">{job_type}</div>
                            <div style="background:#6c63ff22;color:#a89fff;padding:0.2rem 0.6rem;border-radius:20px;font-size:0.7rem;font-weight:600;border:1px solid #6c63ff44">via {source}</div>
                        </div>
                    </div>
                    <div style="display:flex;gap:1.2rem;margin-top:0.6rem;flex-wrap:wrap;font-size:0.8rem">
                        <span style="color:#6b6b80">📍 {location}</span>
                        <span style="color:#ffd700">💰 {salary}</span>
                        <span style="color:#6b6b80">📅 {posted}</span>
                    </div>
                    <div style="color:#9b9bb0;font-size:0.8rem;margin-top:0.6rem;line-height:1.5;border-left:2px solid #2a2a3a;padding-left:0.7rem">{desc}</div>
                    <div style="margin-top:0.8rem">
                        <a href="{apply_link}" target="_blank"
                           style="background:linear-gradient(135deg,#6c63ff,#43e97b);color:#fff;
                                  padding:0.4rem 1.2rem;border-radius:20px;text-decoration:none;
                                  font-size:0.8rem;font-weight:600;font-family:'Space Mono',monospace">
                            Apply Now →
                        </a>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Space Mono',monospace;font-size:1.1rem;font-weight:700;
                color:#6c63ff;padding:1rem 0 0.5rem 0;border-bottom:1px solid #2a2a3a;margin-bottom:1.5rem">
        🎯 ResumeAI<br>
        <span style="font-size:0.65rem;color:#6b6b80">v1.0 · KNN + Random Forest</span>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠  Home",
                "🔴  Live Jobs"
    ], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    knn_status = "🟢 Ready" if recommender.is_fitted else "🟡 Needs Data"
    rf_status  = "🟢 Ready" if ats_predictor.is_fitted else "🟡 Sample Mode"
    st.markdown(f"""
    <div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:12px;padding:1rem;font-size:0.8rem;color:#6b6b80">
        <div style="margin-bottom:0.5rem;color:#e8e8f0;font-weight:600">System Status</div>
        <div>🟢 App Running</div>
        <div>🟢 SQLite Connected</div>
        <div>{knn_status} · KNN Model</div>
        <div>{rf_status} · Random Forest</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HOME PAGE — Analyze Resume built in
# ─────────────────────────────────────────────
if "Home" in page:

    # ── Hero Banner ──
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">🤖 ML-POWERED · KNN + RANDOM FOREST</div>
        <h1 class="hero-title">AI Resume &<br>Job Matcher</h1>
        <p class="hero-sub">Upload your resume · Detect skills · Get real live Indian job recommendations instantly</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Row ──
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:2rem">
        <div class="metric-card"><div class="metric-icon">🧠</div><div class="metric-num">2</div><div class="metric-label">ML Models Active</div></div>
        <div class="metric-card"><div class="metric-icon">⚡</div><div class="metric-num">150+</div><div class="metric-label">Skills Tracked</div></div>
        <div class="metric-card"><div class="metric-icon">🔴</div><div class="metric-num">Live</div><div class="metric-label">Job Recommendations</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── How It Works ──
    st.markdown('<div class="section-header">⚙️ How It Works</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    steps = [
        ("01", "📤", "Upload Resume",  "PDF or DOCX"),
        ("02", "🔍", "Parse Skills",   "Auto-detected"),
        ("03", "🤖", "KNN Match",      "Role classified"),
        ("04", "📊", "Skill Analysis", "Gap identified"),
        ("05", "💼", "Job Preference", "10 live jobs shown"),
    ]
    for col, (num, icon, title, desc) in zip([c1, c2, c3, c4, c5], steps):
        with col:
            st.markdown(f"""
            <div class="info-pill">
                <div style="font-size:1.5rem">{icon}</div>
                <div style="font-family:'Space Mono',monospace;font-size:0.65rem;color:#6b6b80;margin:0.3rem 0">{num}</div>
                <div style="font-weight:700;font-size:0.85rem">{title}</div>
                <div style="font-size:0.75rem;color:#6b6b80;margin-top:0.2rem">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Analyze Resume Section ──
    st.markdown("""
    <h2 style="font-size:1.8rem;font-weight:800;margin:1rem 0 0.3rem 0">📊 Analyze Your Resume</h2>
    <p style="color:#6b6b80;margin:0 0 1.5rem 0">Upload your resume and get 10 live Indian job recommendations matched to your skills</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown('<div class="section-header">📤 Input</div>', unsafe_allow_html=True)
        candidate_name = st.text_input("Your Name", placeholder="e.g. Rahul Sharma")
        uploaded_file  = st.file_uploader("Resume (PDF or DOCX)", type=["pdf", "docx"])
        st.markdown("**— or enter skills manually —**")
        manual_skills  = st.text_area("Skills (comma separated)", placeholder="python, sql, pandas, machine learning...", height=100)

    with col2:
        if uploaded_file or manual_skills.strip():
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                resume_data      = parse_resume(tmp_path)
                skills           = resume_data["skills"]
                experience_years = resume_data["experience_years"]
                education_level  = resume_data["education_level"]
                os.unlink(tmp_path)
            else:
                skills           = [s.strip().lower() for s in manual_skills.split(",") if s.strip()]
                experience_years = 0
                education_level  = 1

            if skills:
                exp_label = 'FRESHER' if experience_years == 0 else 'MID' if experience_years <= 2 else 'SENIOR'

                # ── Detect Best Role dynamically from skills ──
                role_map = {
                    "autocad":"MECHANICAL","solidworks":"MECHANICAL","catia":"MECHANICAL",
                    "ansys":"MECHANICAL","cad":"MECHANICAL","cnc":"MECHANICAL",
                    "manufacturing":"MECHANICAL","hvac":"MECHANICAL","automobile":"MECHANICAL",
                    "thermodynamics":"MECHANICAL","robotics":"MECHANICAL",
                    "electrical":"ELECTRICAL","plc":"ELECTRICAL","scada":"ELECTRICAL",
                    "power systems":"ELECTRICAL","vlsi":"ELECTRICAL","verilog":"ELECTRICAL",
                    "pcb":"ELECTRICAL","power electronics":"ELECTRICAL","solar":"ELECTRICAL",
                    "matlab":"ELECTRICAL",
                    "embedded":"EMBEDDED / IOT","iot":"EMBEDDED / IOT","arduino":"EMBEDDED / IOT",
                    "raspberry pi":"EMBEDDED / IOT","microcontroller":"EMBEDDED / IOT","fpga":"EMBEDDED / IOT",
                    "signal processing":"ELECTRONICS","rf":"ELECTRONICS","circuit":"ELECTRONICS",
                    "civil":"CIVIL","structural":"CIVIL","revit":"CIVIL","construction":"CIVIL","staad":"CIVIL",
                    "chemical":"CHEMICAL","process engineering":"CHEMICAL","piping":"CHEMICAL",
                    "machine learning":"DATA SCIENCE","deep learning":"DATA SCIENCE","data science":"DATA SCIENCE",
                    "nlp":"DATA SCIENCE","computer vision":"DATA SCIENCE",
                    "generative ai":"AI / ML","llm":"AI / ML","mlops":"AI / ML",
                    "python":"SOFTWARE DEV","java":"SOFTWARE DEV","javascript":"SOFTWARE DEV",
                    "react":"SOFTWARE DEV","full stack":"SOFTWARE DEV",
                    "devops":"DEVOPS","aws":"CLOUD","docker":"DEVOPS",
                    "android":"MOBILE DEV","flutter":"MOBILE DEV",
                    "finance":"FINANCE","marketing":"MARKETING","business analyst":"BUSINESS",
                }
                best_role = "ENGINEER"
                for skill in skills:
                    for keyword, role in role_map.items():
                        if keyword in skill or skill in keyword:
                            best_role = role
                            break
                    if best_role != "ENGINEER":
                        break

                # ── Summary Card ──
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#0f0f1a,#1a1030);
                            border:1px solid #2a2a3a;border-radius:16px;padding:1.5rem;
                            margin-bottom:1.5rem;position:relative;overflow:hidden">
                    <div style="position:absolute;top:0;left:0;right:0;height:3px;
                                background:linear-gradient(90deg,#6c63ff,#43e97b)"></div>
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem">
                        <div>
                            <div style="font-size:0.7rem;color:#6b6b80;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem">Skills Detected</div>
                            <div style="font-size:2.5rem;font-weight:800;color:#ffd700;font-family:'Space Mono',monospace">{len(skills)}</div>
                        </div>
                        <div>
                            <div style="font-size:0.7rem;color:#6b6b80;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem">Best Role</div>
                            <div style="font-size:1.3rem;font-weight:700;color:#6c63ff;font-family:'Space Mono',monospace">{best_role}</div>
                        </div>
                        <div>
                            <div style="font-size:0.7rem;color:#6b6b80;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem">Top Skill</div>
                            <div style="font-size:1.1rem;font-weight:700;color:#43e97b;font-family:'Space Mono',monospace">{skills[0].upper() if skills else 'N/A'}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Detected Skills ──
                st.markdown('<div class="section-header">✅ Detected Skills</div>', unsafe_allow_html=True)
                skills_html = "".join([f'<span class="skill-tag">{s}</span>' for s in skills])
                st.markdown(f'<div style="margin-bottom:1.5rem">{skills_html}</div>', unsafe_allow_html=True)

                # ── Job Preference Selector ──
                st.markdown('<div class="section-header">💼 Job Preference</div>', unsafe_allow_html=True)
                st.markdown('<p style="color:#6b6b80;font-size:0.85rem;margin:-0.5rem 0 0.8rem 0">Select the job role you want — we will find real live openings for you</p>', unsafe_allow_html=True)

                JOB_OPTIONS = {
                    "🔧 Mechanical Engineer":        "Mechanical Engineer India",
                    "⚡ Electrical Engineer":         "Electrical Engineer India",
                    "🔌 Embedded / IoT Engineer":    "Embedded IoT Engineer India",
                    "📡 Electronics Engineer":        "Electronics Engineer India",
                    "🏗️ Civil Engineer":              "Civil Engineer India",
                    "⚗️ Chemical Engineer":           "Chemical Engineer India",
                    "🤖 ML / AI Engineer":            "Machine Learning AI Engineer India",
                    "📊 Data Scientist":              "Data Scientist India",
                    "📈 Data Analyst":                "Data Analyst India",
                    "💻 Software Developer":          "Software Developer India",
                    "🌐 Full Stack Developer":        "Full Stack Developer India",
                    "☁️ DevOps / Cloud Engineer":     "DevOps Cloud Engineer India",
                    "📱 Mobile App Developer":        "Mobile App Developer India",
                    "🔐 Cybersecurity Engineer":      "Cybersecurity Engineer India",
                    "🏭 PLC / Automation Engineer":   "PLC SCADA Automation Engineer India",
                    "🔬 R&D / Research Engineer":     "Research Development Engineer India",
                    "🛞 Automobile Engineer":         "Automobile Engineer India",
                    "☀️ Renewable Energy Engineer":   "Renewable Energy Solar Engineer India",
                    "🧱 Structural Engineer":         "Structural Engineer India",
                    "🏢 Project Manager":             "Project Manager Engineering India",
                }

                # Auto-detect best role from skills to set default index
                skill_to_pref = {
                    "machine learning":   "📊 Data Scientist",
                    "deep learning":      "📊 Data Scientist",
                    "data science":       "📊 Data Scientist",
                    "generative ai":      "🤖 ML / AI Engineer",
                    "llm":                "🤖 ML / AI Engineer",
                    "mlops":              "🤖 ML / AI Engineer",
                    "data analyst":       "📈 Data Analyst",
                    "powerbi":            "📈 Data Analyst",
                    "tableau":            "📈 Data Analyst",
                    "autocad":            "🔧 Mechanical Engineer",
                    "solidworks":         "🔧 Mechanical Engineer",
                    "catia":              "🔧 Mechanical Engineer",
                    "ansys":              "🔧 Mechanical Engineer",
                    "cnc":                "🔧 Mechanical Engineer",
                    "hvac":               "🔧 Mechanical Engineer",
                    "plc":                "⚡ Electrical Engineer",
                    "scada":              "⚡ Electrical Engineer",
                    "vlsi":               "⚡ Electrical Engineer",
                    "pcb":                "⚡ Electrical Engineer",
                    "embedded":           "🔌 Embedded / IoT Engineer",
                    "arduino":            "🔌 Embedded / IoT Engineer",
                    "iot":                "🔌 Embedded / IoT Engineer",
                    "microcontroller":    "🔌 Embedded / IoT Engineer",
                    "civil":              "🏗️ Civil Engineer",
                    "structural":         "🧱 Structural Engineer",
                    "revit":              "🏗️ Civil Engineer",
                    "chemical":           "⚗️ Chemical Engineer",
                    "react":              "🌐 Full Stack Developer",
                    "nodejs":             "🌐 Full Stack Developer",
                    "django":             "💻 Software Developer",
                    "flutter":            "📱 Mobile App Developer",
                    "android":            "📱 Mobile App Developer",
                    "devops":             "☁️ DevOps / Cloud Engineer",
                    "aws":                "☁️ DevOps / Cloud Engineer",
                    "docker":             "☁️ DevOps / Cloud Engineer",
                    "automobile":         "🛞 Automobile Engineer",
                    "solar":              "☀️ Renewable Energy Engineer",
                }
                detected_pref = "📊 Data Scientist"  # default
                for skill in skills:
                    for keyword, pref in skill_to_pref.items():
                        if keyword in skill or skill in keyword:
                            detected_pref = pref
                            break
                    if detected_pref != "📊 Data Scientist":
                        break

                job_options_list = list(JOB_OPTIONS.keys())
                default_idx = job_options_list.index(detected_pref) if detected_pref in job_options_list else 0
                job_pref = st.selectbox("Choose your preferred job role", job_options_list, index=default_idx, label_visibility="collapsed")
                api_query = JOB_OPTIONS[job_pref]
                num_results = st.selectbox("Number of jobs to show", [5, 10, 15, 20], index=1)
                fetch_clicked = st.button("🔍 Find Jobs for Me", use_container_width=True)

                if not fetch_clicked:
                    st.markdown("""<div style="background:#111118;border:2px dashed #2a2a3a;border-radius:12px;padding:2rem;text-align:center;color:#6b6b80;margin-top:0.5rem"><div style="font-size:2rem">💼</div><div style="margin-top:0.5rem">Select your job preference above and click Find Jobs</div></div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f'''<div class="section-header">🔴 Live Jobs — {job_pref}<span style="font-size:0.75rem;color:#6b6b80;font-weight:400;margin-left:0.5rem">· searching: <span style="color:#43e97b">{api_query}</span></span></div>''', unsafe_allow_html=True)

                if fetch_clicked:
                    with st.spinner("🔄 Fetching live jobs for your preference..."):
                        try:
                            url      = "https://jsearch.p.rapidapi.com/search"
                            headers  = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}
                            params   = {"query": api_query, "page": "1", "num_pages": "1", "country": "in", "date_posted": "month"}
                            response = requests.get(url, headers=headers, params=params, timeout=15)
                            data     = response.json()
                            if "data" in data and len(data["data"]) > 0:
                                live_jobs = data["data"][:num_results]
                                st.markdown(f'''<div style="background:#0f1a0f;border:1px solid #43e97b33;border-radius:12px;padding:0.7rem 1.2rem;margin-bottom:1rem;display:flex;align-items:center;gap:1rem"><div style="width:8px;height:8px;border-radius:50%;background:#43e97b;box-shadow:0 0 8px #43e97b"></div><span style="color:#43e97b;font-weight:700">{len(live_jobs)} Live Jobs Found</span><span style="color:#6b6b80;font-size:0.82rem">&nbsp;· Updated just now · LinkedIn, Indeed, Glassdoor</span></div>''', unsafe_allow_html=True)
                                render_live_job_cards(live_jobs)
                            else:
                                st.warning("⚠️ No live jobs found right now. Try again in a moment.")
                        except requests.exceptions.Timeout:
                            st.error("⏱️ Request timed out. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Could not fetch live jobs: {str(e)}")

            else:
                st.info("No skills detected. Try entering skills manually.")
        else:
            st.markdown("""
            <div style="background:#111118;border:2px dashed #2a2a3a;border-radius:16px;
                        padding:4rem;text-align:center;color:#6b6b80;margin-top:2rem">
                <div style="font-size:4rem">📄</div>
                <div style="font-size:1.1rem;font-weight:600;color:#e8e8f0;margin:1rem 0 0.5rem 0">Upload your resume to begin</div>
                <div style="font-size:0.85rem">Supports PDF and DOCX · Get 10 live job recommendations instantly</div>
            </div>""", unsafe_allow_html=True)



# ─────────────────────────────────────────────
# LIVE JOBS PAGE
# ─────────────────────────────────────────────
elif "Live Jobs" in page:
    st.markdown("""
    <h2 style="font-size:2rem;font-weight:800;margin:0 0 0.3rem 0">🔴 Live Jobs</h2>
    <p style="color:#6b6b80;margin:0 0 2rem 0">Real-time Indian jobs from LinkedIn, Indeed & Glassdoor</p>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        search_query = st.selectbox("Job Category", [
            # ── Mechanical ──
            "Mechanical Engineer India",
            "Design Engineer CAD India",
            "Manufacturing Engineer India",
            "Automobile Engineer India",
            "HVAC Engineer India",
            "CNC Machinist Engineer India",
            "Robotics Engineer India",
            "Tool Design Engineer India",
            "Quality Control Engineer India",
            "Production Engineer India",
            "Piping Design Engineer India",
            # ── Electrical ──
            "Electrical Engineer India",
            "PLC SCADA Engineer India",
            "Power Systems Engineer India",
            "VLSI Design Engineer India",
            "PCB Design Engineer India",
            "Power Electronics Engineer India",
            "Instrumentation Engineer India",
            "Control Systems Engineer India",
            # ── Electronics / ECE ──
            "Electronics Engineer India",
            "Embedded Systems Engineer India",
            "IoT Engineer India",
            "FPGA Engineer India",
            "RF Engineer India",
            "Signal Processing Engineer India",
            # ── Civil ──
            "Civil Engineer India",
            "Structural Engineer India",
            "Construction Engineer India",
            "BIM Revit Engineer India",
            "Geotechnical Engineer India",
            "Highway Engineer India",
            "Quantity Surveyor India",
            # ── Chemical ──
            "Chemical Engineer India",
            "Process Engineer India",
            "Refinery Engineer India",
            "Safety Engineer India",
            # ── Energy ──
            "Renewable Energy Engineer India",
            "Solar Energy Engineer India",
            "Wind Energy Engineer India",
            # ── AI / ML / Data ──
            "Data Scientist India",
            "Machine Learning Engineer India",
            "AI Engineer India",
            "Deep Learning Engineer India",
            "NLP Engineer India",
            "Computer Vision Engineer India",
            "Generative AI Engineer India",
            "MLOps Engineer India",
            "Data Analyst India",
            "Business Intelligence Analyst India",
            # ── Software / IT ──
            "Software Engineer India",
            "Full Stack Developer India",
            "Python Developer India",
            "Java Developer India",
            "React Developer India",
            "DevOps Engineer India",
            "Cloud Engineer AWS India",
            "Cybersecurity Engineer India",
            "Android Developer India",
            "Flutter Developer India",
            # ── Management / Other ──
            "Project Manager Engineering India",
            "R&D Engineer India",
            "Technical Support Engineer India",
        ])
    with f2:
        city = st.selectbox("City", [
            "Any", "Bangalore", "Mumbai", "Delhi",
            "Hyderabad", "Pune", "Chennai", "Kolkata", "Noida", "Gurgaon"
        ])
    with f3:
        num_jobs = st.selectbox("Number of Jobs", [5, 10, 15, 20])

    if st.button("🔍 Search Live Jobs", use_container_width=True):
        query = search_query if city == "Any" else f"{search_query} {city}"
        with st.spinner("🔄 Fetching live jobs..."):
            try:
                url      = "https://jsearch.p.rapidapi.com/search"
                headers  = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}
                params   = {"query": query, "page": "1", "num_pages": "1", "country": "in", "date_posted": "month"}
                response = requests.get(url, headers=headers, params=params, timeout=15)
                data     = response.json()

                if "data" in data and len(data["data"]) > 0:
                    live_jobs = data["data"][:num_jobs]
                    st.markdown(f"""
                    <div style="background:#0f1a0f;border:1px solid #43e97b33;border-radius:12px;
                                padding:0.8rem 1.5rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem">
                        <div style="width:8px;height:8px;border-radius:50%;background:#43e97b;box-shadow:0 0 8px #43e97b"></div>
                        <span style="color:#43e97b;font-weight:700">{len(live_jobs)} Live Jobs Found</span>
                        <span style="color:#6b6b80;font-size:0.82rem">· Updated just now · LinkedIn, Indeed, Glassdoor</span>
                    </div>
                    """, unsafe_allow_html=True)
                    render_live_job_cards(live_jobs)
                else:
                    st.warning("⚠️ No jobs found. Try a different category or city.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.markdown("""
        <div style="background:#111118;border:2px dashed #2a2a3a;border-radius:16px;
                    padding:4rem;text-align:center;color:#6b6b80;margin-top:1rem">
            <div style="font-size:4rem;margin-bottom:1rem">🔍</div>
            <div style="font-size:1.1rem;font-weight:600;color:#e8e8f0;margin-bottom:0.5rem">Search Live Indian Jobs</div>
            <div style="font-size:0.85rem;color:#6b6b80">Select job category and city above · Click Search · Get real jobs instantly</div>
            <div style="margin-top:1.5rem;display:flex;justify-content:center;gap:1rem;flex-wrap:wrap">
                <span style="background:#6c63ff22;color:#a89fff;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.78rem;border:1px solid #6c63ff44">LinkedIn</span>
                <span style="background:#43e97b22;color:#43e97b;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.78rem;border:1px solid #43e97b44">Indeed</span>
                <span style="background:#ff658422;color:#ff9eb5;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.78rem;border:1px solid #ff658444">Glassdoor</span>
                <span style="background:#ffd70022;color:#ffd700;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.78rem;border:1px solid #ffd70044">Naukri</span>
            </div>
        </div>
        """, unsafe_allow_html=True)