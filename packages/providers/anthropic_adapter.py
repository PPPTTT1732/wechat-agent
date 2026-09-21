import json
import os
from anthropic import AsyncAnthropic
from packages.providers.base import AgentProvider
from packages.agent_core.contracts import ExecutionBrief, WorkerResult

class AnthropicWorkerAdapter(AgentProvider):
    """
    Worker utilisant l'API Anthropic (Claude).
    Idéal pour le code Frontend, le tool-use et WeChat.
    """
    def __init__(self, model_name: str = "claude-3-7-sonnet-20250219"):
        self.model_name = model_name
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def execute_task(self, brief: ExecutionBrief, workspace_path: str) -> WorkerResult:
        system_prompt = (
            "Tu es un ingénieur logiciel expert WeChat. "
            "Tu dois respecter strictement le cahier des charges (Brief) fourni et ne jamais halluciner."
        )
        
        user_prompt = f"""
        EXECUTION BRIEF:
        {brief.model_dump_json(indent=2)}
        
        INSTRUCTION: 
        Retourne UNIQUEMENT un objet JSON valide correspondant au format :
        {{
            "changes": [{{"file": "path", "diff": "code"}}],
            "tests": [{{"name": "test", "passed": true}}]
        }}
        """
        
        # Appel asynchrone à l'API Claude
        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        raw_response = response.content[0].text
        
        # Nettoyage si Claude a ajouté des balises markdown ```json
        if raw_response.startswith("```json"):
            raw_response = raw_response.split("```json")[1].split("```")[0].strip()
        elif raw_response.startswith("```"):
            raw_response = raw_response.split("```")[1].strip()
            
        data = json.loads(raw_response)
        
        # 🛡️ Cast rigoureux dans notre contrat Pydantic (WorkerResult)
        return WorkerResult(
            status="completed",
            provider="anthropic",
            model=self.model_name,
            changes=data.get("changes", []),
            tests=data.get("tests", []),
            logs="Exécution Anthropic terminée avec succès."
        )
