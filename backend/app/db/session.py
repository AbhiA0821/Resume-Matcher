from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Base class for declarative SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Create SQLAlchemy engine for MySQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Session factory for creating database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# FastAPI dependency to obtain a DB session per request
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
