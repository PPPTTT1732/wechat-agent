from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

class TaskRequest(BaseModel):
    """Requête entrante du développeur"""
    task_id: str = Field(..., description="ID unique de la tâche")
    user_id: str = Field(..., description="Développeur ayant initié la tâche")
    project_id: str = Field(..., description="Contexte du projet (isolation)")
    organization_id: str = Field(..., description="Contexte de l'organisation (multi-tenant)")
    prompt: str = Field(..., description="La demande brute du développeur")
    created_at: datetime = Field(default_factory=utcnow)

class ExecutionBrief(BaseModel):
    """Le cahier des charges généré par le WeChat Specialist pour le Worker"""
    task: Dict[str, Any]
    project_context: Dict[str, Any]
    wechat_context: Dict[str, Any]
    known_patterns: List[str] = Field(default_factory=list)
    known_errors: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    security_requirements: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    validation_plan: List[str] = Field(default_factory=list)

class WorkerResult(BaseModel):
    """Le résultat de l'exécution d'un adaptateur IA (Claude, Codex, etc.)"""
    status: str = Field(..., description="'completed' ou 'failed'")
    provider: str = Field(..., description="ex: 'openai', 'anthropic', 'antigravity'")
    model: str
    changes: List[Dict[str, str]] = Field(default_factory=list, description="Fichiers modifiés")
    tests: List[Dict[str, Any]] = Field(default_factory=list, description="Résultats des tests")
    logs: str = ""

class ReviewResult(BaseModel):
    """Le résultat de la validation par le Reviewer"""
    status: str = Field(..., description="'approved', 'needs_correction', ou 'rejected'")
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    wechat_checks: Dict[str, bool] = Field(default_factory=dict)
    security_checks: Dict[str, bool] = Field(default_factory=dict)

class LearningEvent(BaseModel):
    """Un événement d'apprentissage pour la base de connaissance"""
    event_id: str
    type: str = Field(..., description="ex: 'validated_experience', 'error_encountered'")
    source: str = Field(..., description="ex: 'agent_run', 'user_feedback'")
    task_id: str
    project_id: str
    problem: str
    solution: str
    reusable: bool = False
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utcnow)
