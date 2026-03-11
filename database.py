# database.py - SQLite Database Module
import sqlite3
import pandas as pd
import os

DB_PATH = "data/resume_matcher.db"

def get_connection():
    """Get SQLite connection"""
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():
    """Create all required tables"""
    conn = get_connection()
    cursor = conn.cursor()

    # Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            company TEXT,
            required_skills TEXT,
            experience_level TEXT,
            job_role TEXT,
            description TEXT
        )
    ''')

    # Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            resume_skills TEXT,
            ats_score REAL,
            experience_level TEXT,
            job_role TEXT,
            matched_jobs TEXT,
            missing_skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Tables created successfully!")

def load_jobs_from_csv(csv_path):
    """Load job descriptions from CSV into SQLite"""
    conn = get_connection()
    try:
        df = pd.read_csv(csv_path)
        df.to_sql("jobs", conn, if_exists="replace", index=False)
        print(f"Loaded {len(df)} jobs into database!")
    except Exception as e:
        print(f"Error loading CSV: {e}")
    finally:
        conn.close()

def get_all_jobs():
    """Get all jobs from database"""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM jobs", conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

def save_result(candidate_name, resume_skills, ats_score,
                experience_level, job_role, matched_jobs, missing_skills):
    """Save analysis result to database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO results (candidate_name, resume_skills, ats_score,
                             experience_level, job_role, matched_jobs, missing_skills)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        candidate_name,
        ", ".join(resume_skills),
        ats_score,
        experience_level,
        job_role,
        str(matched_jobs),
        ", ".join(missing_skills)
    ))
    conn.commit()
    conn.close()

def get_all_results():
    """Get all saved results"""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM results ORDER BY created_at DESC", conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

# Initialize tables on import
create_tables()
