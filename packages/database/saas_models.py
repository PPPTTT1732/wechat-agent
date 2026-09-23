from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from packages.database.models import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False) # Ex: "Orange", "Afritrips"
    github_org_id = Column(String, nullable=True) # Si on veut lier carrément toute une orga GitHub
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Authentification GitHub (Plus de mot de passe !)
    github_id = Column(String, unique=True, nullable=False)
    github_username = Column(String, nullable=False)
    email = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    role = Column(String, nullable=False, default="DEV") # "ADMIN" ou "DEV"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ApiToken(Base):
    __tablename__ = "api_tokens"
    id = Column(String, primary_key=True) # Ex: "wechat_sk_12345..."
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String) # Ex: "MacBook de Thomas"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
