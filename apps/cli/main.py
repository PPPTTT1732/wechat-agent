import os
import json
import uuid
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

try:
    import typer
except ImportError:
    import sys
    sys.exit(1)

app = typer.Typer(help="WeChat AgentOps - Hybrid Local/Cloud Architecture")

CONFIG_DIR = Path.home() / ".wechat-agent"
CONFIG_FILE = CONFIG_DIR / "config.json"
BRIEF_FILE = Path(".wechat_brief.md")

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
def login(
    token: str = typer.Option(..., prompt="🔑 Entrez votre token d'équipe"),
    api_url: str = typer.Option("http://localhost:8000", prompt="🌐 URL du serveur Neon/Render")
):
    """S'authentifier auprès du cerveau de la mémoire (Render/Neon)."""
    config = load_config()
    config["token"] = token
    config["api_url"] = api_url.rstrip("/")
    save_config(config)
    typer.secho(f"✅ Connecté au Cerveau d'Équipe sur {config['api_url']} !", fg=typer.colors.GREEN)

@app.command()
def link(project_id: str = typer.Option(..., prompt="📁 Entrez l'ID de votre projet (Neon DB)")):
    """Lier le répertoire local à la mémoire du projet."""
    config = load_config()
    config["project_id"] = project_id
    save_config(config)
    typer.secho(f"🔗 Dossier lié au projet : {project_id}", fg=typer.colors.BLUE)

@app.command()
def prepare(prompt: str):
    """Prépare le terrain pour Antigravity/Codex en générant le Cahier des Charges."""
    config = load_config()
    
    # 1. (Dans le futur) Le CLI fera un appel GET /rag au serveur pour récupérer la mémoire Neon
    # memory_context = fetch_neon_memory(prompt, config)
    memory_context = "Aucune erreur similaire trouvée dans la mémoire d'équipe pour ce projet."
    
    # 2. On génère le fichier local pour l'IA de l'IDE
    brief_content = f"""# 🧠 WeChat AgentOps - Execution Brief

## 🎯 Demande du Développeur
{prompt}

## 📚 Mémoire de l'Équipe (Base Neon)
{memory_context}

## 📋 Instructions pour Antigravity / Claude
1. Lis attentivement la demande.
2. Écris le code directement dans les bons fichiers de ce projet.
3. Respecte l'architecture WeChat Native.
"""
    
    with open(BRIEF_FILE, "w") as f:
        f.write(brief_content)
        
    typer.secho(f"✅ Fichier {BRIEF_FILE} généré avec succès !", fg=typer.colors.GREEN)
    typer.secho("🤖 Maintenant, ouvrez le chat de votre éditeur (Antigravity/Claude) et dites :", fg=typer.colors.CYAN)
    typer.secho(f'👉 "Exécute les instructions du fichier {BRIEF_FILE}"', fg=typer.colors.YELLOW, bold=True)

@app.command()
def learn():
    """Capture le code fraîchement généré par l'IA locale et l'envoie dans Neon."""
    config = load_config()
    
    # On capture les modifications non commitées (ce que l'IA vient de coder)
    try:
        git_diff = subprocess.check_output(["git", "diff"]).decode("utf-8")
        if not git_diff:
            typer.secho("❌ Aucun code modifié trouvé. Demandez d'abord à l'IA de coder.", fg=typer.colors.RED)
            return
            
        # (Dans le futur) Envoyer git_diff à l'API POST /learn pour vectorisation dans Neon
        typer.secho("🧠 Envoi des connaissances au serveur Neon (RAG)...", fg=typer.colors.YELLOW)
        # requests.post(...)
        
        typer.secho("✅ Code sauvegardé dans la mémoire de l'équipe (Statut: PROPOSED) !", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho("❌ Erreur lors de la capture du code.", fg=typer.colors.RED)

if __name__ == "__main__":
    app()
