# Import all SQLAlchemy models here for Alembic metadata discovery
from app.db.session import Base
from app.models.user import User
from app.models.resume import Resume

__all__ = ["Base", "User", "Resume"]
