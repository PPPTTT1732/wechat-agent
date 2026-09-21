import json
from packages.agent_core.contracts import TaskRequest, ExecutionBrief
from packages.wechat_specialist.prompts import SPECIALIST_SYSTEM_PROMPT

class WechatSpecialist:
    """
    Le cerveau superviseur de la plateforme (Phase 7).
    Il orchestre l'analyse RAG et rédige le cahier des charges (Brief) pour le Worker.
    """
    
    def __init__(self, llm_client, retriever, code_scanner):
        """
        Injection des dépendances : 
        - llm_client : L'API LLM (souvent un modèle rapide/structuré comme Haiku ou gpt-4o-mini)
        - retriever : Le moteur de recherche Vectoriel (pgvector)
        - code_scanner : L'analyseur Tree-sitter du repository
        """
        self.llm_client = llm_client
        self.retriever = retriever
        self.code_scanner = code_scanner

    async def prepare_execution_brief(self, request: TaskRequest) -> ExecutionBrief:
        # 1. Analyse du projet en temps réel (Code Intelligence - Phase 6)
        # Retourne ex: {"framework": "Taro", "language": "TypeScript", "architecture": "feature-based"}
        project_context = await self.code_scanner.analyze_project(request.project_id)
        
        # 2. RAG : Recherche dans la mémoire vectorielle (Phase 5)
        # Recherche hybride dans les niveaux 1 (Global), 2 (Org), et 3 (Projet)
        knowledge = await self.retriever.search_memory(
            query=request.prompt,
            organization_id=request.organization_id,
            project_id=request.project_id,
            top_k=5
        )
        
        # 3. Construction du prompt enrichi pour le LLM Superviseur
        prompt_content = f"""
        TÂCHE DEMANDÉE : {request.prompt}
        
        CONTEXTE DU PROJET (Code Intelligence) : 
        {json.dumps(project_context, indent=2)}
        
        CONNAISSANCE RÉCUPÉRÉE (RAG Memory) : 
        {json.dumps(knowledge, indent=2)}
        
        INSTRUCTION : Génère le JSON ExecutionBrief.
        """
        
        # 4. Génération de la spécification par le LLM Superviseur
        response_text = await self.llm_client.generate_json(
            system_prompt=SPECIALIST_SYSTEM_PROMPT,
            user_prompt=prompt_content
        )
        
        # 5. Validation Pydantic absolue
        # Si le LLM a mal structuré le JSON, Pydantic va lever une erreur 
        # (que le système pourra catch pour faire un auto-retry).
        raw_dict = json.loads(response_text)
        brief = ExecutionBrief(**raw_dict)
        
        # Injection des métadonnées statiques
        brief.task["task_id"] = request.task_id
        brief.task["original_prompt"] = request.prompt
        
        return brief
