import os
import json
import uuid
import urllib.request
import urllib.error
from pathlib import Path

# Typer est déjà dans nos dépendances (inclus via FastAPI/Pydantic ou ajouté via pip)
# S'il manque en production, pip install typer s'en chargera.
try:
    import typer
except ImportError:
    import sys
    print("Typer n'est pas installé. Lancez: pip install typer")
    sys.exit(1)

app = typer.Typer(help="WeChat Engineering Agent - CLI (Phase 30)")

CONFIG_DIR = Path.home() / ".wechat-agent"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

@app.command()
def login(token: str = typer.Option(..., prompt="🔑 Entrez votre token (ex: DEV_TOKEN_ORG_A)")):
    """S'authentifier auprès de l'API AgentOps."""
    config = load_config()
    config["token"] = token
    config["api_url"] = "http://localhost:8000"
    save_config(config)
    typer.secho("✅ Connecté avec succès à la plateforme AgentOps !", fg=typer.colors.GREEN)

@app.command()
def link(project_id: str = typer.Option(..., prompt="📁 Entrez l'ID de votre projet (Neon DB)")):
    """Lier le répertoire local à un projet de la plateforme."""
    config = load_config()
    config["project_id"] = project_id
    save_config(config)
    typer.secho(f"🔗 Dossier courant lié au projet : {project_id}", fg=typer.colors.BLUE)

@app.command()
def ask(prompt: str):
    """Demander à l'IA de résoudre un problème ou d'ajouter une feature."""
    config = load_config()
    token = config.get("token")
    project_id = config.get("project_id")
    api_url = config.get("api_url", "http://localhost:8000")

    if not token or not project_id:
        typer.secho("❌ Erreur : Vous devez lancer 'wechat-agent login' puis 'wechat-agent link'.", fg=typer.colors.RED)
        raise typer.Exit(1)

    task_id = str(uuid.uuid4())
    
    # Contrat d'interface strict (Phase 01)
    payload = json.dumps({
        "task_id": task_id,
        "user_id": "cli_developer",
        "project_id": project_id,
        "organization_id": "ignored_by_api", # Écrasé côté serveur par le JWT pour la sécurité
        "prompt": prompt
    }).encode('utf-8')

    req = urllib.request.Request(f"{api_url}/api/v1/tasks/")
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')

    try:
        typer.secho("🚀 Envoi de la tâche au WeChat Specialist (RAG)...", fg=typer.colors.YELLOW)
        response = urllib.request.urlopen(req, payload)
        result = json.loads(response.read())
        
        typer.secho(f"✅ Tâche acceptée ! ID: {result['task_id']}", fg=typer.colors.GREEN)
        typer.secho("🛠️  Le Worker Celery travaille dessus en arrière-plan. Vous recevrez une notification quand le code sera prêt.", fg=typer.colors.CYAN)
        
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        typer.secho(f"❌ Erreur API: {e.code} - {error_msg}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()
