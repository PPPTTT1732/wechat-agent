from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import shutil
import tempfile
import subprocess
from packages.database.session import get_db
from packages.database.sonatel_models import MemoryChunk, AgentSkill

router = APIRouter(prefix="/api/v1/memory", tags=["Memory & Ingestion"])

class IngestRequest(BaseModel):
    url: str
    project_id: str = "default"

EXTENSIONS_AUTORISEES = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".wxml", ".wxss", ".wxs", ".json",
    ".md", ".yaml", ".yml"
}
DOSSIERS_IGNORES = {"node_modules", ".git", ".venv", "__pycache__", "dist", "build", ".next", ".vercel"}

def process_github_repo(url: str, project_id: str, db: Session):
    dossier_temp = tempfile.mkdtemp(prefix="agentops_ingest_")
    try:
        # Cloner le dépôt
        subprocess.run(["git", "clone", "--depth=1", url, dossier_temp], check=True, capture_output=True)
        
        # Scanner les fichiers
        for racine, dossiers, fichiers in os.walk(dossier_temp):
            dossiers[:] = [d for d in dossiers if d not in DOSSIERS_IGNORES]
            for fichier in fichiers:
                _, ext = os.path.splitext(fichier)
                if ext not in EXTENSIONS_AUTORISEES:
                    continue
                
                chemin_complet = os.path.join(racine, fichier)
                chemin_relatif = os.path.relpath(chemin_complet, dossier_temp)
                
                try:
                    with open(chemin_complet, "r", encoding="utf-8", errors="ignore") as f:
                        contenu = f.read()
                    
                    if len(contenu.strip()) < 50:
                        continue
                        
                    # 3000 chars par chunk (basique)
                    chunks = [contenu[i:i+3000] for i in range(0, len(contenu), 3000)]
                    for chunk in chunks:
                        texte = f"# Source: {url}\n# Fichier: {chemin_relatif}\n\n{chunk}"
                        db_chunk = MemoryChunk(
                            project_id=project_id,
                            content=texte,
                            metadata_json={"source": url, "file": chemin_relatif},
                            status="PROPOSED" # L'Admin devra valider dans le Cerveau
                        )
                        db.add(db_chunk)
                        
                except Exception:
                    pass
        db.commit()
    except subprocess.CalledProcessError:
        pass # Silencieux en asynchrone, mais pourrait stocker une erreur
    finally:
        shutil.rmtree(dossier_temp, ignore_errors=True)


@router.post("/ingest-github")
def ingest_github_url(req: IngestRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Lance l'ingestion d'un dépôt Git en tâche de fond.
    Les morceaux de code seront enregistrés avec le statut 'PROPOSED'.
    """
    if not (req.url.startswith("http://") or req.url.startswith("https://")):
        raise HTTPException(status_code=400, detail="URL Git invalide")
    
    background_tasks.add_task(process_github_repo, req.url, req.project_id, db)
    return {"message": "Ingestion démarrée en arrière-plan. Le Cerveau va se remplir dans quelques instants."}


class SkillRequest(BaseModel):
    title: str
    description: str
    author: str = "Admin"

@router.get("/skills")
def get_skills(db: Session = Depends(get_db)):
    skills = db.query(AgentSkill).order_by(AgentSkill.id.desc()).all()
    return skills

@router.post("/skills")
def create_skill(req: SkillRequest, db: Session = Depends(get_db)):
    skill = AgentSkill(
        title=req.title,
        description=req.description,
        author=req.author
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill
