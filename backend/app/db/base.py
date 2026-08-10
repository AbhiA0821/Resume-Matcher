# Import all SQLAlchemy models here for Alembic metadata discovery
from app.db.session import Base
from app.models.user import User

__all__ = ["Base", "User"]
