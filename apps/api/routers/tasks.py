from fastapi import APIRouter, BackgroundTasks
from packages.agent_core.contracts import TaskRequest

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

@router.post("/")
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Point d'entrée principal : Reçoit la demande du développeur, 
    l'enregistre et la délègue au système d'orchestration en arrière-plan.
    """
    # ÉTAPE FUTURE :
    # 1. Sauvegarder dans la DB Neon (AgentRun status = pending)
    # 2. Envoyer au Worker Celery : orchestrate_agent_workflow.delay(request.model_dump())
    
    return {
        "status": "queued",
        "task_id": request.task_id,
        "message": "La tâche a été mise en file d'attente pour le WeChat Specialist."
    }

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """Permet au client (Web/CLI/VSCode) de vérifier l'avancement de la tâche."""
    # ÉTAPE FUTURE : Lire le statut depuis la base de données
    return {
        "task_id": task_id,
        "status": "pending"
    }
