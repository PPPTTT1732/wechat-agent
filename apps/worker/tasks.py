from apps.worker.celery_app import celery_app
from packages.database.session import SessionLocal

from packages.code_intelligence.scanner import ProjectScanner
import time

@celery_app.task(bind=True, name="orchestrate_agent_task")
def orchestrate_agent_task(self, task_request_dict: dict):
    task_id = task_request_dict.get("task_id")
    project_id = task_request_dict.get("project_id")
    
    db = SessionLocal()
    agent_run = None
    try:
        # 1. Enregistrer le lancement
        agent_run = AgentRun(
            task_id=task_id, project_id=project_id,
            provider="pending", model="pending", status="running"
        )
        db.add(agent_run)
        
        # Récupération de l'URL GitHub du projet (Étape 08)
        project = db.query(Project).filter(Project.id == project_id).first()
        repo_url = project.repository_url if project else "local"
        db.commit()

        # 2. CODE INTELLIGENCE ENGINE (Phase 09)
        scanner = ProjectScanner()
        # [Ici se trouvera le git clone du repo_url vers un dossier /tmp/]
        
        # Le scanner lit le dossier et produit le contexte exact (Taro, JS, TS, etc.)
        project_context = scanner.analyze_workspace_mock(repo_url)
        print(f"[SCANNER] ADN du projet détecté : {project_context}")
        
        # 3. WECHAT SPECIALIST (Phase 07)
        # Il prendra ce contexte et l'enverra au LLM pour rédiger le ExecutionBrief...
        time.sleep(2) # Simulation de réflexion IA
        
        # 4. Succès de la tâche
        agent_run.status = "success"
        db.commit()
        
        return {"status": "success", "context_detected": project_context}
        
    except Exception as e:
        db.rollback()
        if agent_run:
            agent_run.status = "failed"
            db.commit()
        raise e
    finally:
        db.close()
