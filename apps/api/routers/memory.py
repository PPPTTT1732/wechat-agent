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

@router.post("/learn")
def learn_from_code(req: LearnRequest, db: Session = Depends(get_db)):
    """Convertit le code en vecteur et l'enregistre dans Neon (Statut PROPOSED)."""
    try:
        if not req.diff_content or len(req.diff_content) < 10:
            return {"status": "ignored", "message": "Diff trop court"}

        vector = get_huggingface_embedding(req.diff_content)

        chunk = KnowledgeChunk(
            project_id=req.project_id,
            content=req.diff_content,
            embedding=vector
        )
        db.add(chunk)
        db.commit()

        return {"status": "success", "message": "Code vectorisé et sauvegardé avec succès."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur learn: {str(e)}")

@router.post("/prepare")
def prepare_context(req: PrepareRequest, db: Session = Depends(get_db)):
    """Recherche dans la base vectorielle Neon les solutions précédentes similaires."""
    try:
        vector = get_huggingface_embedding(req.prompt)
        # Casting pgvector correct : utilisation du type ::vector
        vector_literal = "[" + ",".join(str(round(x, 6)) for x in vector) + "]"

        query = text("""
            SELECT content
            FROM knowledge_chunks
            WHERE project_id = :pid
            ORDER BY embedding <=> CAST(:vec AS vector)
            LIMIT 3
        """)

        results = db.execute(query, {"pid": req.project_id, "vec": vector_literal}).fetchall()

        if not results:
            return {"context": "Aucune mémoire spécifique trouvée pour ce projet. Appliquez les règles d'architecture standard."}

        context = "\n\n---\n\n".join([row[0] for row in results])
        return {"context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prepare: {str(e)}")
