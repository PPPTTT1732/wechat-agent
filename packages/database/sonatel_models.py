from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from packages.database.models import Base

class UIComponent(Base):
    __tablename__ = "ui_components"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tags = Column(String)
    author = Column(String)
    initials = Column(String)
    preview = Column(String)
    code = Column(JSON) # {"WXML": "...", "WXSS": "..."}
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DevOpsIncident(Base):
    __tablename__ = "devops_incidents"
    id = Column(Integer, primary_key=True, index=True)
    error_trace = Column(String)
    repo = Column(String)
    time_ago = Column(String)
    status = Column(String)
    tone = Column(String)

class LeaderboardProfile(Base):
    __tablename__ = "leaderboard_profiles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    initials = Column(String)
    score = Column(Integer)
    growth = Column(String)
    badge = Column(String)
    rank = Column(Integer)

class ApiToken(Base):
    __tablename__ = "api_tokens"
    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ComponentCategory(Base):
    __tablename__ = "component_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True)
    email = Column(String)
    name = Column(String)
    role = Column(String, default="USER") # "ADMIN" ou "USER"
    can_ingest = Column(Integer, default=0) # 0 = Non, 1 = Oui (SQLite/Postgres fallback for boolean)
