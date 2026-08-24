import os
import sqlite3
from typing import List, Optional, Dict, Any

# Path calculation to root workspace data/resume_matcher.db
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "data", "resume_matcher.db")

def get_jobs_from_db(
    search: Optional[str] = None,
    role: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Retrieves jobs from SQLite database data/resume_matcher.db with search and filtering support."""
    if not os.path.exists(DB_PATH):
        return {"total": 0, "jobs": []}

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        base_query = "FROM jobs WHERE 1=1"
        params: List[Any] = []

        if search and search.strip():
            term = f"%{search.strip()}%"
            base_query += " AND (job_title LIKE ? OR required_skills LIKE ? OR description LIKE ?)"
            params.extend([term, term, term])

        if role and role.strip():
            roles_list = [r.strip() for r in role.split(",") if r.strip()]
            if roles_list:
                role_conditions = " OR ".join(["job_title LIKE ? OR job_role LIKE ?" for _ in roles_list])
                base_query += f" AND ({role_conditions})"
                for r in roles_list:
                    r_term = f"%{r}%"
                    params.extend([r_term, r_term])

        # Count total matching rows
        count_sql = f"SELECT COUNT(*) {base_query}"
        cursor.execute(count_sql, params)
        count_row = cursor.fetchone()
        total = count_row[0] if count_row else 0

        # Fetch paginated rows
        select_sql = f"SELECT id, job_title, company, required_skills, experience_level, job_role, description {base_query} LIMIT ? OFFSET ?"
        fetch_params = params + [limit, offset]
        cursor.execute(select_sql, fetch_params)
        rows = cursor.fetchall()
        conn.close()

        jobs = [dict(row) for row in rows]
        return {"total": total, "jobs": jobs}
    except Exception as e:
        print(f"Error querying job database: {e}")
        return {"total": 0, "jobs": []}
