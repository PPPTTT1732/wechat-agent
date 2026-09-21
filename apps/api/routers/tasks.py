from fastapi import APIRouter, BackgroundTasks, Depends
from packages.agent_core.contracts import TaskRequest
from packages.security.auth import get_current_user, CurrentUser
from packages.security.dependencies import require_project_access
from packages.database.models import Project

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

@router.post("/")
async def create_task(
    request: TaskRequest, 
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user),
    # L'injection de cette dépendance protège automatiquement la route :
    # Si le user n'a pas accès au request.project_id, FastAPI bloque la requête.
    project: Project = Depends(require_project_access)
):
    """
    Crée une tâche de développement. 
    Entièrement protégée : vérifie le token et les droits sur le projet.
    """
    # Force l'organisation du user connecté pour des raisons de sécurité
    request.organization_id = current_user.organization_id
    request.user_id = current_user.user_id
    
    # ... Logique de file d'attente (Celery) à implémenter plus tard ...
    
    return {
        "status": "queued",
        "task_id": request.task_id,
        "message": f"Tâche acceptée pour le projet {project.name}"
    }

@router.get("/{task_id}")
async def get_task_status(task_id: str, current_user: CurrentUser = Depends(get_current_user)):
    return {
        "task_id": task_id,
        "status": "pending"
    }
