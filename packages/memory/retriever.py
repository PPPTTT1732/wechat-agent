from typing import List, Dict, Any
from sqlalchemy.orm import Session
from packages.database.models import KnowledgeChunk
from packages.database.session import SessionLocal

class EmbeddingService:
    """
    Service d'Embeddings.
    Dans la V2, cette classe appellera l'API OpenAI (text-embedding-3-small) 
    ou Google Gemini pour convertir le texte en vecteur de 768 dimensions.
    """
    async def get_embedding(self, text: str) -> List[float]:
        # TODO: Appeler l'API d'embedding externe.
        # Retourne un vecteur vide (768 dimensions) pour que l'architecture tourne sans bloquer.
        return [0.0] * 768

class MemoryRetriever:
    """
    Phase 11 : Le moteur de recherche Vectorielle (RAG).
    Alimente le WeChat Specialist avec les connaissances du passé.
    """
    def __init__(self):
        self.embedder = EmbeddingService()

    async def search_memory(
        self, 
        query: str, 
        organization_id: str, 
        project_id: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recherche hybride dans Neon PostgreSQL (pgvector).
        """
        # 1. Vectorisation de la question du développeur
        query_vector = await self.embedder.get_embedding(query)
        
        db = SessionLocal()
        try:
            # 2. La requête Magique : RAG + Isolation Multi-Tenant (Phase 5)
            # On cherche les chunks les plus proches sémantiquement, MAIS
            # on filtre impérativement selon le périmètre de l'utilisateur.
            results = (
                db.query(KnowledgeChunk)
                .filter(
                    # Niveau 1 : Connaissance Publique/Globale WeChat (Fournie par la plateforme)
                    (KnowledgeChunk.organization_id.is_(None)) | 
                    # Niveau 2 : Connaissance privée de l'Organisation (Partagée entre tous ses projets)
                    (
                        (KnowledgeChunk.organization_id == organization_id) & 
                        (KnowledgeChunk.project_id.is_(None))
                    ) |
                    # Niveau 3 : Connaissance Ultra-spécifique au projet
                    (KnowledgeChunk.project_id == project_id)
                )
                # On trie par distance cosinus (les plus pertinents en premier)
                .order_by(KnowledgeChunk.embedding.cosine_distance(query_vector))
                .limit(top_k)
                .all()
            )
            
            # 3. Formatage standardisé pour le LLM (WeChat Specialist)
            memory_context = []
            for chunk in results:
                # Identification de la provenance du chunk
                if not chunk.organization_id:
                    level = "Niveau 1 (Global Platform)"
                elif not chunk.project_id:
                    level = "Niveau 2 (Organization Memory)"
                else:
                    level = "Niveau 3 (Project Specific)"
                
                memory_context.append({
                    "provenance": level,
                    "type": chunk.content_type, # 'experience', 'pattern', 'documentation'
                    "status": chunk.status,     # 'trusted', 'validated'
                    "content": chunk.content
                })
                
            return memory_context
            
        except Exception as e:
            print(f"[RAG ERROR] Erreur lors de la recherche vectorielle : {e}")
            return []
        finally:
            db.close()
