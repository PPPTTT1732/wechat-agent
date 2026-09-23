import os
import json
import subprocess
from pathlib import Path

try:
    import typer
    import requests
except ImportError:
    import sys
    sys.exit(1)

app = typer.Typer(help="WeChat AgentOps - Hybrid Local/Cloud Architecture")

CONFIG_DIR = Path.home() / ".wechat-agent"
CONFIG_FILE = CONFIG_DIR / "config.json"
BRIEF_FILE = Path(".wechat_brief.md")

def load_config():
    if not CONFIG_FILE.exists():
        typer.secho("❌ Erreur: Non connecté. Lancez 'wechat-agent login'", fg=typer.colors.RED)
        raise typer.Exit(1)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_config_safe():
    if not CONFIG_FILE.exists(): return {}
    with open(CONFIG_FILE, "r") as f: return json.load(f)

def save_config(config):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

@app.command()
def login(
    token: str = typer.Option(..., prompt="🔑 Entrez votre token d'équipe"),
    api_url: str = typer.Option("http://localhost:8000", prompt="🌐 URL du serveur Neon/Render")
):
    config = load_config_safe()
    config["token"] = token
    config["api_url"] = api_url.rstrip("/")
    save_config(config)
    typer.secho(f"✅ Connecté au serveur sur {config['api_url']}", fg=typer.colors.GREEN)

@app.command()
def link(project_id: str = typer.Option(..., prompt="📁 Entrez l'ID de votre projet (ex: mp-afritrips)")):
    config = load_config_safe()
    config["project_id"] = project_id
    save_config(config)
    typer.secho(f"🔗 Projet lié : {project_id}", fg=typer.colors.BLUE)

@app.command()
def prepare(prompt: str):
    config = load_config()
    if "project_id" not in config:
        typer.secho("❌ Veuillez lier le projet d'abord : 'wechat-agent link'", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    typer.secho("🧠 Consultation de la mémoire d'équipe (Neon DB)...", fg=typer.colors.YELLOW)
    
    # --- LE VRAI APPEL API ---
    api_url = f"{config['api_url']}/api/v1/memory/prepare"
    headers = {"Authorization": f"Bearer {config['token']}"}
    payload = {"project_id": config["project_id"], "prompt": prompt}
    
    try:
        res = requests.post(api_url, headers=headers, json=payload)
        res.raise_for_status()
        memory_context = res.json().get("context", "")
    except Exception as e:
        typer.secho(f"⚠️ Erreur de connexion au serveur : {e}", fg=typer.colors.RED)
        memory_context = "Connexion à la mémoire échouée. Mode hors-ligne."

    brief_content = f"""# 🧠 WeChat AgentOps - Execution Brief

## 🎯 Demande du Développeur
{prompt}

## 📚 Mémoire de l'Équipe (Context RAG)
{memory_context}

## 📋 Instructions pour Antigravity / Claude
1. Lis attentivement la demande et la mémoire de l'équipe ci-dessus.
2. Si un fichier SKILL.md WeChat existe, respecte rigoureusement son architecture.
3. Écris le code directement dans ce projet de manière complète.
"""
    
    with open(BRIEF_FILE, "w") as f:
        f.write(brief_content)
        
    typer.secho(f"✅ Fichier {BRIEF_FILE} généré avec le contexte cloud !", fg=typer.colors.GREEN)
    typer.secho('👉 Demandez à votre IA de l\'exécuter.', fg=typer.colors.CYAN)

@app.command()
def learn():
    config = load_config()
    if "project_id" not in config:
        typer.secho("❌ Projet non lié.", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    try:
        # Capture du code fraîchement modifié/ajouté
        git_diff = subprocess.check_output(["git", "diff", "HEAD"]).decode("utf-8")
        if not git_diff.strip():
            typer.secho("❌ Aucun code modifié n'a été détecté.", fg=typer.colors.RED)
            return
            
        typer.secho("🧠 Envoi des modifications pour vectorisation mathématique...", fg=typer.colors.YELLOW)
        
        # --- LE VRAI APPEL API ---
        api_url = f"{config['api_url']}/api/v1/memory/learn"
        headers = {"Authorization": f"Bearer {config['token']}"}
        payload = {"project_id": config["project_id"], "diff_content": git_diff}
        
        res = requests.post(api_url, headers=headers, json=payload)
        res.raise_for_status()
        
        typer.secho("✅ Code sauvegardé dans la mémoire de l'équipe (Statut: PROPOSED) !", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho(f"❌ Erreur lors de l'apprentissage : {e}", fg=typer.colors.RED)

@app.command()
def review():
    config = load_config()
    if "project_id" not in config:
        typer.secho("❌ Projet non lié.", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    typer.secho(f"🔍 Recherche des propositions en attente pour le projet {config['project_id']}...", fg=typer.colors.CYAN)
    
    api_url = f"{config['api_url']}/api/v1/memory/review?project_id={config['project_id']}"
    headers = {"Authorization": f"Bearer {config['token']}"}
    
    try:
        res = requests.get(api_url, headers=headers)
        res.raise_for_status()
        chunks = res.json()
        
        if not chunks:
            typer.secho("✅ Super ! Il n'y a aucun code en attente de validation.", fg=typer.colors.GREEN)
            return
            
        for chunk in chunks:
            typer.secho("\n====================================", fg=typer.colors.MAGENTA)
            typer.secho("📄 PROPOSITION DE CODE :", fg=typer.colors.YELLOW)
            typer.echo(chunk["content"])
            typer.secho("====================================", fg=typer.colors.MAGENTA)
            
            choice = typer.prompt("Accepter (A), Rejeter (R), Passer (P)", type=str).upper()
            
            if choice == 'A':
                requests.post(f"{config['api_url']}/api/v1/memory/review/{chunk['id']}", headers=headers, json={"status": "TRUSTED"})
                typer.secho("✅ Code approuvé (TRUSTED). Il sera utilisé par le système RAG !", fg=typer.colors.GREEN)
            elif choice == 'R':
                requests.post(f"{config['api_url']}/api/v1/memory/review/{chunk['id']}", headers=headers, json={"status": "REJECTED"})
                typer.secho("🗑️ Code rejeté et supprimé.", fg=typer.colors.RED)
            else:
                typer.secho("⏭️ Proposition ignorée (reste en attente).", fg=typer.colors.BLUE)
                
    except Exception as e:
        typer.secho(f"❌ Erreur réseau : {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()
