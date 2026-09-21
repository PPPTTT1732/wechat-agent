import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

def utcnow():
    return datetime.now(timezone.utc)

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    
    projects = relationship("Project", back_populates="organization")

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    framework = Column(String)  # Ex: 'Taro', 'Native WeChat'
    language = Column(String)   # Ex: 'TypeScript', 'JavaScript'
    repository_url = Column(String)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    
    organization = relationship("Organization", back_populates="projects")
    agent_runs = relationship("AgentRun", back_populates="project")

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    task_id = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    status = Column(String, nullable=False) # 'pending', 'running', 'success', 'failed'
    metrics = Column(JSON) # {"latency_ms": 1200, "cost_usd": 0.04, "tokens": 4000}
    created_at = Column(DateTime(timezone=True), default=utcnow)
    
    project = relationship("Project", back_populates="agent_runs")

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id = Column(String, primary_key=True, default=generate_uuid)
    
    # ─── GESTION DES 3 NIVEAUX DE CONNAISSANCE (Phase 5) ───
    # Si organization_id est NULL -> Niveau 1 (Global WeChat Knowledge)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True) 
    # Si project_id est NULL mais org est défini -> Niveau 2 (Organisation)
    # Si project_id est défini -> Niveau 3 (Projet spécifique)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    
    content = Column(String, nullable=False)
    content_type = Column(String, nullable=False) # 'documentation', 'experience', 'pattern'
    status = Column(String, nullable=False) # 'proposed', 'validated', 'trusted', 'shared'
    confidence = Column(Float, default=0.0)
    
    # pgvector embedding: dimension 768 standard pour beaucoup de modèles text-embedding
    embedding = Column(Vector(768)) 
    
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
