# 🎯 SkillSync AI — Resume Analyzer & Live Job Matcher

A final year portfolio project built using Python, Machine Learning, and Streamlit.  
Upload your resume → Skills get detected automatically → Pick your job preference → Get real live Indian job listings instantly.

### 🌐 Live Demo
Open in Streamlit :  https://resume-matcher-ypjig2msxnqn7dchb2ctg5.streamlit.app

👉 **[Click here to open the app](https://resume-matcher-ypjig2msxnqn7dchb2ctg5.streamlit.app)**

---

## 👨‍💻 Built By

**Abhishek Ainapure**  
3rd Year B.Tech — Artificial Intelligence  
Annasaheb Dange College of Engineering, Ashta  
🔗 GitHub: [github.com/AbhiA0821](https://github.com/AbhiA0821)

---

## 💡 Why I Built This

Most resume tools only work for software or data science jobs. I wanted to build something that works for **every type of engineer** — Mechanical, Electrical, IoT, Civil, Chemical, and more. This project combines resume parsing, machine learning, and a real job API to give useful, practical output to any student or fresher looking for jobs in India.

---

## 🔍 What This Project Does

1. You upload your resume as PDF or DOCX
2. The app reads the entire resume and finds all your skills automatically
3. It detects what type of engineer you are (Mechanical, Data Science, Electrical, etc.)
4. You pick the kind of job you want from a dropdown with 20 job roles
5. The app fetches **real live job listings** from LinkedIn, Indeed, Glassdoor and Naukri
6. You see job cards with company name, location, salary, job type, and a direct Apply Now link

---

## 🖥️ Pages in the App

### 🏠 Home Page
- Hero banner with project title
- Stats cards — ML Models Active, Skills Tracked, Live Jobs
- "How It Works" — 5 step visual guide
- Full resume upload and analysis section built directly on this page

### 🔴 Live Jobs Page
- Manual job search without uploading resume
- Filter by job category (12 options) and Indian city (10 cities)
- Choose how many jobs to show — 5, 10, 15, or 20
- Fetches real jobs on every search click

---

## ✨ Key Features

| Feature | Details |
|---------|---------|
| Resume Parsing | Reads PDF and DOCX files, extracts all text including tables and columns |
| Skill Detection | Matches against 150+ skills across 8+ engineering domains |
| Role Detection | Automatically identifies if you are Mechanical, Electrical, Data Science, IoT etc. |
| Job Preference | Dropdown with 20 job roles — auto-selects the best match based on your skills |
| Live Jobs | Pulls real jobs from LinkedIn, Indeed, Glassdoor, Naukri via JSearch API |
| Job Cards | Shows company logo, title, location, salary, job type, description, Apply Now button |
| Dark UI | Cyberpunk style dark theme — purple and green color scheme, Space Mono font |
| Manual Input | Can also enter skills manually without uploading a resume |

---

## 🧠 Machine Learning

Two ML models are used in this project:

### KNN — K Nearest Neighbors
- Used for job recommendation
- Finds the most similar job roles based on your skill set
- Implemented using scikit-learn

### Random Forest Classifier
- Used for role classification and ATS score prediction
- Trained on a job descriptions dataset
- Gives a confidence score for your best matching role

### Skill Extraction Logic
- Resume text is extracted using pdfplumber (for PDF) and python-docx (for DOCX)
- Text is cleaned, lowercased, and checked against 150+ skill keywords
- Matched skills are passed to the ML models for classification

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| UI Framework | Streamlit |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| Machine Learning | scikit-learn (KNN, Random Forest) |
| Data Handling | Pandas, NumPy |
| Charts | Plotly |
| Live Jobs | JSearch API (RapidAPI) |
| Database | SQLite |
| Language | Python 3.9+ |

---

## 💼 Job Domains Supported

| Domain | Example Skills Detected |
|--------|------------------------|
| Mechanical | AutoCAD, CATIA, SolidWorks, ANSYS, CNC, HVAC, FEA |
| Electrical | PLC, SCADA, VLSI, Verilog, PCB, MATLAB, Power Systems |
| Embedded / IoT | Arduino, Raspberry Pi, ESP32, FPGA, Microcontroller, MQTT |
| Electronics | Signal Processing, RF Design, Circuit Design |
| Civil | Revit, STAAD Pro, BIM, Structural Design, GIS |
| Chemical | Aspen Plus, HYSYS, Piping, Process Engineering |
| Data Science / ML | Python, TensorFlow, PyTorch, NLP, Computer Vision |
| AI / GenAI | LLM, Generative AI, LangChain, Hugging Face, MLOps |
| Software | React, Django, Node.js, Java, Flutter, Docker, AWS |

---

## 📁 Project Structure

```
resume_matcher/
│
├── app.py              ← Main Streamlit app — all pages and UI
├── parser.py           ← Resume text extraction and skill detection
├── matcher.py          ← KNN and Random Forest ML models
├── database.py         ← SQLite database setup
├── requirements.txt    ← Python packages needed
├── README.md           ← This file
│
├── data/
│   └── jobs.csv        ← Sample job dataset used for model training
│
└── models/             ← Auto-created when app runs first time
    ├── knn_recommender.pkl
    └── ats_predictor.pkl
```

---

## ▶️ How to Run Locally

**Step 1 — Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/resume-matcher.git
cd resume-matcher
```

**Step 2 — Install packages**
```bash
pip install -r requirements.txt
```

**Step 3 — Run the app**
```bash
streamlit run app.py
```

**Step 4 — Open in browser**
```
http://localhost:8501
```

---

## 🔑 Live Jobs API

Jobs are fetched using **JSearch API** from RapidAPI which pulls from LinkedIn, Indeed, Glassdoor and Naukri.

- Free plan: 500 requests/month, no credit card needed
- Sign up: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

To use your own key replace this line in `app.py`:
```python
RAPIDAPI_KEY = "your_key_here"
```

---

## 🚀 Deploy Free on Streamlit Cloud

1. Push this project to GitHub
2. Go to https://share.streamlit.io and sign in with GitHub
3. Click **New App** → select this repo → set main file as `app.py`
4. Click **Deploy**

App goes live at `https://your-username-resume-matcher.streamlit.app`

---

## 📌 What I Learned

- Parsing PDF and DOCX files in Python
- Building and training KNN and Random Forest models with scikit-learn
- Integrating a third party REST API (JSearch / RapidAPI) using requests
- Building multi-page Streamlit apps with custom HTML and CSS
- Designing a dark theme UI inside Streamlit
- Building a skill detection system that works across all engineering domains

---
