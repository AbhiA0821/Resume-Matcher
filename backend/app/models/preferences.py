from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class JobPreferences(Base):
    __tablename__ = "job_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    auto_apply_enabled = Column(Boolean, nullable=False, default=False)
    daily_apply_limit = Column(Integer, nullable=False, default=10)
    desired_job_titles = Column(Text, nullable=True)
    preferred_industries = Column(Text, nullable=True)
    min_salary = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="preferences")
