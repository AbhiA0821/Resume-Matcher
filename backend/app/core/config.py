import os
from typing import List
from pydantic_settings import BaseSettings

# Calculate absolute path to backend/.env so it loads regardless of working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "HireAgent API"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
    ]

    # Database configuration for MySQL
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/hireagent"

    class Config:
        case_sensitive = True
        env_file = ENV_FILE_PATH
        extra = "ignore"

settings = Settings()
