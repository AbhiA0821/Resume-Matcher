from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    target_role = Column(String(255), nullable=True)
    experience_level = Column(String(50), nullable=True)
    preferred_locations = Column(Text, nullable=True)
    work_mode_preference = Column(String(50), nullable=True)
    employment_type = Column(String(50), nullable=True)
    min_match_score = Column(Float, nullable=False, default=70.0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="profile")
