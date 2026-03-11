# AI-Powered Resume & Job Matcher
### Built with KNN + Random Forest | Streamlit | SQLite

---

## Project Structure

```
resume_matcher/
│
├── app.py              ← Main Streamlit UI
├── parser.py           ← Resume PDF/DOCX parsing
├── matcher.py          ← KNN + Random Forest ML models
├── database.py         ← SQLite storage
├── requirements.txt    ← All dependencies
│
├── data/
│   └── jobs.csv        ← Sample job descriptions dataset
│
└── models/             ← Saved ML model files (auto created)
    ├── knn_recommender.pkl
    └── ats_predictor.pkl
```

---

## Steps to Run the Project

### Step 1 — Install Python
Make sure Python 3.9 or above is installed.
Check by running: `python --version`

### Step 2 — Open Project in VS Code
- Open VS Code
- Go to File → Open Folder
- Select the `resume_matcher` folder

### Step 3 — Open Terminal in VS Code
- Press `Ctrl + ~` to open terminal

### Step 4 — Install Required Libraries
```bash
pip install -r requirements.txt
```
Wait for all libraries to install. This may take 2-3 minutes.

### Step 5 — Run the App
```bash
streamlit run app.py
```

### Step 6 — Open in Browser
After running, the app opens automatically at:
```
http://localhost:8501
```

---

## How to Use the App

1. Go to **Analyze Resume** page
2. Upload your resume PDF or DOCX file
3. Enter your name
4. Click Analyze
5. See your ATS score, top job matches, and missing skills
6. Click Save Result to store in database

---

## How to Add Your Own Job Dataset

1. Go to **Job Database** page in the app
2. Upload your jobs CSV file
3. CSV must have these columns:
   - job_title
   - company
   - required_skills
   - experience_level
   - job_role

---

## ML Models Used

| Model | Task | Library |
|-------|------|---------|
| KNN | Job Recommendation | scikit-learn |
| Random Forest | ATS Score Prediction | scikit-learn |
| Random Forest | Job Role Classification | scikit-learn |
| TF-IDF | Text Vectorization | scikit-learn |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Resume Parsing | pdfplumber, python-docx |
| Data Processing | Pandas, NumPy |
| ML Models | scikit-learn (KNN, Random Forest) |
| Visualization | Plotly |
| UI | Streamlit |
| Storage | SQLite |
| Dev Environment | VS Code |

---

## Common Errors & Fixes

**Error: ModuleNotFoundError**
→ Run `pip install -r requirements.txt` again

**Error: streamlit not found**
→ Run `pip install streamlit`

**App not opening in browser**
→ Manually open `http://localhost:8501`

**No skills extracted from resume**
→ Use the manual skill input box instead

---

## How to Create ZIP File in VS Code

1. Open VS Code terminal (`Ctrl + ~`)
2. Navigate to parent folder of your project
3. Run this command:
```bash
# On Windows
Compress-Archive -Path resume_matcher -DestinationPath resume_matcher.zip

# On Mac/Linux
zip -r resume_matcher.zip resume_matcher/
```
4. ZIP file will be created in the same folder

---

Made with Python, scikit-learn, and Streamlit
