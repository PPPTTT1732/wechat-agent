from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from packages.security.auth import get_current_user, CurrentUser
from packages.database.session import get_db
from packages.database.models import Project

def require_project_access(
    project_id: str, 
    current_user: CurrentUser = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Mur de sécurité Multi-Tenant (Phase 06).
    Vérifie en base de données que le projet demandé appartient bien
    à l'organisation de l'utilisateur qui fait la requête.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")
        
    if project.organization_id != current_user.organization_id:
        # 🔒 SEC-01 : On lève une 404 (et non une 403 Forbidden) 
        # pour éviter qu'un attaquant découvre l'existence des projets des autres entreprises.
        raise HTTPException(status_code=404, detail="Projet introuvable")
        
    return project
