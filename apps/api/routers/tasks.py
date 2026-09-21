from fastapi import APIRouter, BackgroundTasks, Depends
from packages.agent_core.contracts import TaskRequest
from packages.security.auth import get_current_user, CurrentUser
from packages.security.dependencies import require_project_access
from packages.database.models import Project

# IMPORT CRUCIAL : La tâche Celery
from apps.worker.tasks import orchestrate_agent_task

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

@router.post("/")
async def create_task(
    request: TaskRequest, 
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user),
    project: Project = Depends(require_project_access)
):
    """
    Protégé par JWT et Multi-Tenant.
    Délègue la lourde charge de l'IA au Worker Celery en arrière-plan.
    """
    request.organization_id = current_user.organization_id
    request.user_id = current_user.user_id
    
    # ENVOI MAGIQUE DANS LA FILE D'ATTENTE REDIS (Asynchrone)
    # request.model_dump() transforme l'objet Pydantic en dictionnaire JSON-serializable
    orchestrate_agent_task.delay(request.model_dump())
    
    return {
        "status": "queued",
        "task_id": request.task_id,
        "message": f"Tâche acceptée pour le projet {project.name}. Le Worker a pris le relais."
    }

@router.get("/{task_id}")
async def get_task_status(task_id: str, current_user: CurrentUser = Depends(get_current_user)):
    # Bientôt : on lira 'AgentRun' dans la base Neon
    return {
        "task_id": task_id,
        "status": "pending_or_running"
    }
