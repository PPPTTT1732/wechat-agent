from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from packages.shared.schemas import ProjectCreate, ProjectResponse
from packages.database.session import get_db
from packages.database.models import Project
from packages.security.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Déclare un nouveau dépôt Git WeChat dans la plateforme.
    Il est automatiquement verrouillé sur l'Organisation du développeur.
    """
    new_project = Project(
        organization_id=current_user.organization_id,
        name=project_data.name,
        framework=project_data.framework,
        language=project_data.language,
        repository_url=project_data.repository_url
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Renvoie la liste des projets.
    GARANTIE MULTI-TENANT : Le filtre SQLAlchemy bloque l'accès aux autres orgs.
    """
    projects = db.query(Project).filter(
        Project.organization_id == current_user.organization_id
    ).all()
    
    return projects
