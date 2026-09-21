from typing import NamedTuple
from packages.agent_core.contracts import ExecutionBrief

class ProviderSelection(NamedTuple):
    provider_name: str
    model_name: str
    reason: str

class ModelRouter:
    """
    Route intelligemment une tâche vers le meilleur LLM selon le contexte (Phase 9).
    Initialement basé sur des règles statiques. Évoluera vers du routage par historique (ML).
    """
    
    def select_provider(self, brief: ExecutionBrief) -> ProviderSelection:
        task_type = brief.task.get("type", "feature")
        complexity = brief.task.get("complexity", "medium")
        requires_sandbox = brief.task.get("requires_sandbox", False)
        
        # Règle 1 : Tâche large autonome nécessitant une sandbox Linux complète
        if complexity == "high" or requires_sandbox:
            return ProviderSelection(
                provider_name="antigravity",
                model_name="gemini-3.1-pro",
                reason="Tâche complexe nécessitant sandbox Linux et exécution autonome (Web/Fichiers)"
            )
        
        # Règle 2 : Refactoring complexe ou architecture pointue
        if task_type in ["architecture", "refactoring"]:
            return ProviderSelection(
                provider_name="openai",
                model_name="o1-preview",
                reason="Tâche de conception nécessitant un raisonnement profond (Reasoning/Codex)"
            )
            
        # Règle 3 : Création de features WeChat / UI / Fix (Tool-use)
        if task_type in ["feature", "bugfix", "ui_integration"]:
            return ProviderSelection(
                provider_name="anthropic",
                model_name="claude-3-7-sonnet",
                reason="Excellente capacité de tool-use et manipulation de code Frontend"
            )
            
        # Fallback par défaut (Tâche mineure / Débogage simple)
        return ProviderSelection(
            provider_name="anthropic",
            model_name="claude-3-5-haiku",
            reason="Tâche mineure, optimisation ratio coût/latence"
        )
