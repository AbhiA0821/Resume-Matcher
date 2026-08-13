🤖 HireAgent
Agentic RAG for Resume & Job Analysis
HireAgent is an AI-powered career assistant designed to understand resumes and job descriptions, find meaningful matches, and provide personalized career insights using modern AI Engineering techniques.
🎯 What It Does
```text
User
 ↓
Login / Google Sign-In
 ↓
Upload Resume
 ↓
Extract Text
 ↓
Chunk Text
 ↓
Embeddings
 ↓
Vector Database
 ↓
Semantic Search / HNSW
 ↓
RAG
 ↓
LLM
 ↓
Multi-Agent Analysis
 ↓
Job & Career Insights
```
The goal is to move beyond simple keyword matching and understand the meaning and context of resumes and jobs.
✨ Main Features
🔐 Email/password authentication with JWT
🔥 Google authentication with Firebase
🗄️ MySQL database with SQLAlchemy & Alembic
📄 Resume upload and text extraction
🧠 Semantic embeddings
🔎 Vector similarity search with HNSW
📚 Retrieval Augmented Generation (RAG)
🤖 LLM-powered analysis
🤝 Multi-agent career analysis
🧬 Genetic-algorithm-based optimization
💼 Resume and job analysis
> AI features marked in the roadmap are added phase-by-phase and are not all implemented yet.
🏗️ Architecture
```text
Frontend
   ↓
FastAPI Backend
   ↓
Authentication ─────── MySQL
   ↓
Resume Processing
   ↓
Embeddings
   ↓
Vector Database
   ↓
HNSW Search
   ↓
RAG
   ↓
LLM
   ↓
Multi-Agent System
   ↓
Career / Job Analysis
```
🛠️ Tech Stack
Area	Technologies
Backend	Python, FastAPI, Uvicorn
Database	MySQL, SQLAlchemy, Alembic, PyMySQL
Authentication	JWT, Firebase Authentication, Google Sign-In
AI	Embeddings, Vector DB, HNSW, RAG, LLM/Gemini, Multi-Agent AI
Existing App	Streamlit, SQLite
Tools	Git, GitHub, VS Code
📁 Project Structure
```text
HireAgent/
├── app.py
├── parser.py
├── matcher.py
├── database.py
├── load_data.py
├── data/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   └── uploads/
├── .gitignore
└── README.md
```
🔌 Current API
```text
GET  /health
GET  /api/v1/health

POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/firebase
GET  /api/v1/auth/me

POST /api/v1/resumes
GET  /api/v1/resumes
GET  /api/v1/resumes/{resume_id}

GET  /api/v1/profile
PUT  /api/v1/profile
GET  /api/v1/preferences
PUT  /api/v1/preferences
```
API documentation:
```text
http://localhost:8000/docs
```
⚙️ Local Setup
```bash
git clone https://github.com/AbhiA0821/HireAgent.git
cd HireAgent

py -3.12 -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```
Create the MySQL database:
```sql
CREATE DATABASE hireagent;
```
Configure `backend/.env` with database, JWT, and Firebase settings.
Run migrations:
```bash
py -m alembic -c backend/alembic.ini upgrade head
```
Start the backend:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
🧪 Engineering & Security
Passwords are securely hashed.
JWT protects authenticated APIs.
Firebase tokens are verified by the backend.
Users can access only their own resources.
Database changes are managed with Alembic.
Secrets and Firebase credentials are excluded from Git.
Existing Streamlit functionality is preserved.
🗺️ Roadmap
Phase	Feature	Status
1	FastAPI Foundation	✅
2	MySQL + SQLAlchemy + Alembic	✅
3	JWT Authentication	✅
4	Firebase Google Authentication	✅
5	Resume Management	✅
6	Text Processing & Chunking	✅
7	User Profile & Job Preferences Engine	✅
8	Embeddings	⏳
9	Vector Database	⏳
10	HNSW / Semantic Search	⏳
11	LLM / Gemini	⏳
12	RAG	⏳
13	Multi-Agent System	⏳
14	Genetic Algorithm	⏳
15	Job Analysis & Matching	⏳
16	Frontend	⏳
17	Deployment	⏳
📌 Current Status
Active development — Phase 7 Completed
Completed:
`FastAPI` • `MySQL` • `JWT` • `Firebase Google Authentication` • `Resume Management` • `User Profile & Job Preferences Engine`

Next major AI stages:
`Chunking → Embeddings → Vector DB → HNSW → RAG → LLM → Multi-Agent AI`
👨‍💻 Author
Abhi  
B.Tech Artificial Intelligence & Data Science
GitHub: https://github.com/AbhiA0821
---
⭐ HireAgent — From Resume Matching to Agentic RAG Career Intelligence.