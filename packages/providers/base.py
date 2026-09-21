from typing import Protocol, runtime_checkable
from packages.agent_core.contracts import ExecutionBrief, WorkerResult

@runtime_checkable
class AgentProvider(Protocol):
    """
    Interface standard pour tous les LLMs/Agents utilisés comme Workers (Phase 8).
    Que ce soit Claude, Codex ou Antigravity, ils doivent respecter ce contrat absolu.
    """
    
    async def execute_task(self, brief: ExecutionBrief, workspace_path: str) -> WorkerResult:
        """
        Fait exécuter la tâche par l'agent dans un environnement isolé.
        
        Args:
            brief: Le cahier des charges strict (généré par le WeChat Specialist).
            workspace_path: Le chemin absolu vers le dossier isolé contenant le code (sandbox).
            
        Returns:
            WorkerResult: Un compte rendu standardisé contenant le statut, les fichiers modifiés et les logs.
        """
        ...
