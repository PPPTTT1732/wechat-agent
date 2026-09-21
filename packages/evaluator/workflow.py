import json
from packages.agent_core.contracts import ExecutionBrief, WorkerResult, ReviewResult
from packages.prompts.evaluator.prompts import REVIEWER_SYSTEM_PROMPT

class ReviewerAgent:
    """
    Phase 12 : Le moteur de Review.
    Garde-fou qui vérifie la qualité et la sécurité du code généré.
    """
    def __init__(self, llm_client):
        # L'évaluateur nécessite souvent un modèle "Reasoning" très fort (ex: o1-preview ou GPT-4o)
        self.llm_client = llm_client

    async def evaluate_execution(self, brief: ExecutionBrief, worker_result: WorkerResult) -> ReviewResult:
        # 1. Vérifications statiques rapides (Sans IA)
        if worker_result.status == "failed":
            return ReviewResult(
                status="rejected",
                issues=[{"type": "worker_crash", "message": worker_result.logs}],
                wechat_checks={"compiled": False},
                security_checks={"executed_safely": False}
            )
        
        # 2. Construction du contexte d'évaluation pour le LLM Juge
        prompt_content = f"""
        CAHIER DES CHARGES INITIAL (Brief) :
        {brief.model_dump_json(indent=2)}
        
        CODE PRODUIT PAR LE WORKER (Result) :
        {worker_result.model_dump_json(indent=2)}
        
        INSTRUCTION : Génère le JSON ReviewResult pour évaluer rigoureusement ce travail.
        """
        
        # 3. Examen par l'IA Juge
        response_text = await self.llm_client.generate_json(
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            user_prompt=prompt_content
        )
        
        # 4. Validation Pydantic pour garantir le format du contrat (Phase 01)
        raw_dict = json.loads(response_text)
        review = ReviewResult(**raw_dict)
        
        return review
