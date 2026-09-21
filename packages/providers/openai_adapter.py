import json
import os
from openai import AsyncOpenAI
from packages.providers.base import AgentProvider
from packages.agent_core.contracts import ExecutionBrief, WorkerResult

class OpenAIWorkerAdapter(AgentProvider):
    """
    Worker utilisant l'API OpenAI.
    Idéal pour les tâches d'architecture complexe (Modèles Reasoning o1/o3).
    """
    def __init__(self, model_name: str = "o1-preview"):
        self.model_name = model_name
        # L'API Key est lue depuis l'environnement
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def execute_task(self, brief: ExecutionBrief, workspace_path: str) -> WorkerResult:
        system_prompt = (
            "Tu es un ingénieur logiciel autonome. "
            "Ton but est de générer du code selon ce cahier des charges strict."
        )
        
        user_prompt = f"""
        EXECUTION BRIEF (Cahier des charges généré par le WeChat Specialist):
        {brief.model_dump_json(indent=2)}
        
        INSTRUCTION: 
        Retourne UNIQUEMENT un objet JSON valide correspondant au format :
        {{
            "changes": [{{"file": "path", "diff": "code"}}],
            "tests": [{{"name": "test", "passed": true}}]
        }}
        """
        
        # Appel asynchrone à l'API OpenAI
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        raw_response = response.choices[0].message.content
        data = json.loads(raw_response)
        
        # 🛡️ Cast rigoureux dans notre contrat Pydantic (WorkerResult)
        return WorkerResult(
            status="completed",
            provider="openai",
            model=self.model_name,
            changes=data.get("changes", []),
            tests=data.get("tests", []),
            logs="Exécution OpenAI terminée avec succès."
        )
