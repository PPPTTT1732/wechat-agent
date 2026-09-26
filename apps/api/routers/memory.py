from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from packages.database.session import get_db
from packages.database.models import KnowledgeChunk
from packages.providers.embeddings import get_huggingface_embedding

router = APIRouter(prefix="/api/v1/memory", tags=["Memory"])

class LearnRequest(BaseModel):
    project_id: str
    diff_content: str

class PrepareRequest(BaseModel):
    project_id: str
    prompt: str

class ReviewDecision(BaseModel):
    status: str

@router.post("/learn")
def learn_from_code(req: LearnRequest, db: Session = Depends(get_db)):
    """Convertit le code en vecteur et l'enregistre (Statut PROPOSED)."""
    try:
        if not req.diff_content or len(req.diff_content) < 10:
            return {"status": "ignored", "message": "Diff trop court"}

        vector = get_huggingface_embedding(req.diff_content)

        chunk = KnowledgeChunk(
            project_id=req.project_id,
            content=req.diff_content,
            embedding=vector,
            status="PROPOSED" # Par défaut
        )
        db.add(chunk)
        db.commit()

        return {"status": "success", "message": "Code vectorisé et sauvegardé (En attente de validation)."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur learn: {str(e)}")

@router.post("/prepare")
def prepare_context(req: PrepareRequest, db: Session = Depends(get_db)):
    """Recherche les solutions (Retrieval) puis génère localement (Anti-Crash Mode)."""
    try:
        vector = get_huggingface_embedding(req.prompt)
        vector_literal = "[" + ",".join(str(round(x, 6)) for x in vector) + "]"

        query = text("""
            SELECT content
            FROM knowledge_chunks
            WHERE project_id = :pid AND status = 'TRUSTED'
            ORDER BY embedding <=> CAST(:vec AS vector)
            LIMIT 5
        """)

        results = db.execute(query, {"pid": req.project_id, "vec": vector_literal}).fetchall()

        if not results:
            return {"context": "Aucune mémoire validée trouvée pour ce projet. Appliquez les règles d'architecture standard."}

        raw_context = "\n---\n".join([row[0] for row in results])

        # Moteur RAG : utilise toujours les vrais résultats de la recherche vectorielle
        answer = f"Voici ce que j'ai trouvé dans la mémoire officielle du projet **mp-afritrips** :\n\n```text\n{raw_context[:1200]}\n```"

        final_response = f"🤖 **AgentOps AI (Jumeau Numérique Sonatel)**\n\n{answer}"

        return {"context": final_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prepare: {str(e)}")









@router.get("/review")
def get_proposed_chunks(project_id: str, db: Session = Depends(get_db)):
    """Récupère tous les codes en attente de validation."""
    query = text("SELECT id, content FROM knowledge_chunks WHERE project_id = :pid AND status = 'PROPOSED'")
    results = db.execute(query, {"pid": project_id}).fetchall()
    return [{"id": str(r[0]), "content": str(r[1])} for r in results]

@router.post("/review/{chunk_id}")
def submit_review(chunk_id: str, decision: ReviewDecision, db: Session = Depends(get_db)):
    """Le Lead Dev accepte (TRUSTED) ou rejette (supprime) un code."""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk introuvable")
        
    if decision.status == "REJECTED":
        db.delete(chunk)
    else:
        chunk.status = decision.status
        
    db.commit()
    return {"status": "success"}

@router.get("/dashboard/chunks")
def get_all_chunks(project_id: str, db: Session = Depends(get_db)):
    """API pour le Dashboard : Récupère toute la mémoire (tous statuts)."""
    query = text("SELECT id, content, status, metadata_json, created_at FROM knowledge_chunks WHERE project_id = :pid ORDER BY created_at DESC")
    results = db.execute(query, {"pid": project_id}).fetchall()
    return [{
        "id": str(r[0]),
        "content": str(r[1]),
        "status": str(r[2]),
        "metadata": r[3] if r[3] else {},
        "created_at": r[4].isoformat() if r[4] else None
    } for r in results]

class UpdateChunkRequest(BaseModel):
    content: str = None
    status: str = None
    metadata: dict = None

@router.patch("/dashboard/chunks/{chunk_id}")
def update_chunk(chunk_id: str, req: UpdateChunkRequest, req_obj: Request, db: Session = Depends(get_db)):
    require_admin(req_obj)
    """API pour le Dashboard : Modifie un chunk (texte, statut, tags)."""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk introuvable")
    
    if req.content is not None:
        chunk.content = req.content
        # Optionnel: Re-vectoriser si le contenu change beaucoup
    if req.status is not None:
        chunk.status = req.status
    if req.metadata is not None:
        chunk.metadata_json = req.metadata
        
    db.commit()
    return {"status": "success"}

from fastapi import Request
import base64
import json

# Stockage temporaire pour la démo : le 1er connecté devient le Lead Dev (ADMIN)
ADMIN_USER_ID = None

def get_clerk_user_id(req: Request):
    auth = req.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ")[1]
    try:
        # Décodage rapide du payload JWT (dans le vrai SaaS, on vérifiera la signature cryptographique)
        payload = token.split(".")[1]
        payload += "=" * ((4 - len(payload) % 4) % 4)
        decoded = json.loads(base64.b64decode(payload).decode('utf-8'))
        return decoded.get("sub") # l'ID Clerk (ex: user_2...)
    except:
        return None

@router.get("/dashboard/me")
def get_my_role(req: Request):
    global ADMIN_USER_ID
    user_id = get_clerk_user_id(req)
    if not user_id:
        raise HTTPException(status_code=401, detail="Non connecté")
    
    # Le premier utilisateur qui appelle cette route devient l'Admin !
    if ADMIN_USER_ID is None:
        ADMIN_USER_ID = user_id
        
    role = "ADMIN" if user_id == ADMIN_USER_ID else "DEV"
    return {"role": role, "user_id": user_id}

# On sécurise la modification des chunks !
def require_admin(req: Request):
    global ADMIN_USER_ID
    user_id = get_clerk_user_id(req)
    if not user_id or user_id != ADMIN_USER_ID:
        raise HTTPException(status_code=403, detail="Accès refusé : Rôle ADMIN requis.")
    return user_id

