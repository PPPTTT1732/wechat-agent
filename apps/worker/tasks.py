from apps.worker.celery_app import celery_app
from packages.database.session import SessionLocal
from packages.database.models import AgentRun
import time

@celery_app.task(bind=True, name="orchestrate_agent_task")
def orchestrate_agent_task(self, task_request_dict: dict):
    """
    C'est ici que l'agent vit en arrière-plan.
    task_request_dict est le modèle Pydantic TaskRequest converti en dictionnaire.
    """
    task_id = task_request_dict.get("task_id")
    project_id = task_request_dict.get("project_id")
    
    db = SessionLocal()
    agent_run = None
    try:
        # 1. Mise à jour DB Neon : L'agent démarre
        agent_run = AgentRun(
            task_id=task_id, 
            project_id=project_id,
            provider="routing...", # En attente du Model Router
            model="routing...",
            status="running"
        )
        db.add(agent_run)
        db.commit()

        # --- PIPELINE DE L'AGENT ---
        # Ici viendront s'emboîter les prochaines phases :
        # - Code Intelligence (git clone)
        # - WeChat Specialist (RAG + ExecutionBrief)
        # - Model Router (Sélection du LLM)
        # - AgentProvider (Génération du code)
        
        print(f"[WORKER] Démarrage de la tâche {task_id} pour le projet {project_id}")
        time.sleep(2) # Simulation temporaire d'un travail d'IA
        
        # 2. L'agent a terminé avec succès
        agent_run.status = "success"
        db.commit()
        
        return {"status": "success", "task_id": task_id}
        
    except Exception as e:
        db.rollback()
        if agent_run:
            agent_run.status = "failed"
            db.commit()
        raise e
    finally:
        db.close()
