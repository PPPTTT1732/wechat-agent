from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from packages.database.models import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True)
    email = Column(String)
    name = Column(String)
    role = Column(String, default="USER") # "ADMIN" ou "USER"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
