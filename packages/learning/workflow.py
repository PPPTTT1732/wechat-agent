import json
import uuid
from sqlalchemy.orm import Session
from packages.agent_core.contracts import TaskRequest, WorkerResult, LearningEvent
from packages.database.models import KnowledgeChunk
from packages.database.session import SessionLocal
from packages.prompts.learning.prompts import LEARNING_SYSTEM_PROMPT
from packages.memory.retriever import EmbeddingService

class LearningAgent:
    """
    Phases 13 & 14 : Le moteur d'apprentissage continu et le Pipeline de confiance.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.embedder = EmbeddingService()

    async def extract_and_store_learning(
        self, 
        request: TaskRequest, 
        worker_result: WorkerResult
    ) -> LearningEvent:
        
        # 1. Préparation du contexte d'extraction
        prompt_content = f"""
        PROBLÈME / DEMANDE (TaskRequest) :
        {request.prompt}
        
        SOLUTION IMPLÉMENTÉE (WorkerResult Changes) :
        {json.dumps(worker_result.changes, indent=2)}
        """
        
        # 2. IA génératrice de la leçon (Synthèse)
        response_text = await self.llm_client.generate_json(
            system_prompt=LEARNING_SYSTEM_PROMPT,
            user_prompt=prompt_content
        )
        
        raw_dict = json.loads(response_text)
        
        # Injection des métadonnées structurelles
        raw_dict["event_id"] = str(uuid.uuid4())
        raw_dict["task_id"] = request.task_id
        raw_dict["project_id"] = request.project_id
        raw_dict["type"] = "validated_experience"
        raw_dict["source"] = "agent_run"
        
        learning_event = LearningEvent(**raw_dict)
        
        # 3. PIPELINE DE CONFIANCE (Phase 14) : Sauvegarde dans Neon
        # Si la leçon est jugée pertinente par l'IA, on la stocke.
        if learning_event.reusable and learning_event.confidence >= 0.7:
            db = SessionLocal()
            try:
                # Vectorisation du texte pour la recherche sémantique (RAG)
                text_to_embed = f"Problème: {learning_event.problem} | Solution: {learning_event.solution}"
                embedding = await self.embedder.get_embedding(text_to_embed)
                
                chunk = KnowledgeChunk(
                    organization_id=request.organization_id,
                    project_id=request.project_id, # Niveau 3: Isolé au projet
                    content=json.dumps({"problem": learning_event.problem, "solution": learning_event.solution}),
                    content_type="experience",
                    # 🔒 SEC-02 : Jamais "trusted" par défaut. Attend la validation d'un Lead Dev.
                    status="proposed", 
                    confidence=learning_event.confidence,
                    embedding=embedding
                )
                db.add(chunk)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"[LEARNING ERROR] {e}")
            finally:
                db.close()
        
        return learning_event
