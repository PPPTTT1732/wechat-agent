#!/usr/bin/env python3
"""
🧠 AgentOps — Script d'ingestion universelle
=============================================
Nourrit le Cerveau IA avec n'importe quel projet.

UTILISATION :
  # Depuis une URL GitHub / GitLab
  python3 ingest_project.py https://github.com/MalickDevWeb/Niatta mon-projet-v1

  # Depuis un dossier local
  python3 ingest_project.py /home/pmt/Téléchargements/mp-afritrips mp-afritrips-v1

  # Depuis un dépôt privé (avec token)
  python3 ingest_project.py https://TOKEN@github.com/org/repo projet-prive-v1
"""

import os
import sys
import shutil
import tempfile
import subprocess
import requests
import time

API_URL = "https://wechat-agent-5y0i.onrender.com/api/v1/memory/learn"

EXTENSIONS_AUTORISEES = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".wxml", ".wxss", ".wxs", ".json",
    ".md", ".txt", ".yaml", ".yml", ".sh",
    ".html", ".css", ".scss", ".vue", ".dart"
}

DOSSIERS_IGNORES = {
    "node_modules", ".git", ".venv", "__pycache__",
    "dist", "build", ".next", ".vercel", "coverage",
    ".idea", ".vscode", "vendor", "tmp", ".cache"
}

def cloner_depuis_git(url: str) -> str:
    """Clone un dépôt Git dans un dossier temporaire et retourne le chemin."""
    dossier_temp = tempfile.mkdtemp(prefix="agentops_ingest_")
    print(f"📥 Clonage de : {url}")
    print(f"📂 Dossier temporaire : {dossier_temp}")

    result = subprocess.run(
        ["git", "clone", "--depth=1", url, dossier_temp],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        shutil.rmtree(dossier_temp, ignore_errors=True)
        print(f"❌ Erreur de clonage : {result.stderr}")
        sys.exit(1)

    print("✅ Clonage réussi !\n")
    return dossier_temp

def scanner_et_envoyer(chemin_projet: str, project_id: str, nettoyer_apres: bool = False):
    """Scanne récursivement un projet et envoie chaque fichier au cerveau."""
    print(f"🧠 Ingestion du projet : {project_id}")
    print(f"📁 Chemin : {chemin_projet}")
    print("="*60)

    total = 0
    succes = 0
    ignores = 0

    for racine, dossiers, fichiers in os.walk(chemin_projet):
        dossiers[:] = [d for d in dossiers if d not in DOSSIERS_IGNORES]

        for fichier in fichiers:
            _, ext = os.path.splitext(fichier)
            if ext not in EXTENSIONS_AUTORISEES:
                continue

            chemin_complet = os.path.join(racine, fichier)
            chemin_relatif = os.path.relpath(chemin_complet, chemin_projet)

            try:
                with open(chemin_complet, "r", encoding="utf-8", errors="ignore") as f:
                    contenu = f.read()

                if len(contenu.strip()) < 50:
                    ignores += 1
                    continue

                # Envoi par chunks de 3000 caractères max
                chunks = [contenu[i:i+3000] for i in range(0, len(contenu), 3000)]

                for i, chunk in enumerate(chunks):
                    partie = f" (partie {i+1}/{len(chunks)})" if len(chunks) > 1 else ""
                    contenu_enrichi = f"# Fichier: {chemin_relatif}{partie}\n\n{chunk}"

                    response = requests.post(API_URL, json={
                        "project_id": project_id,
                        "diff_content": contenu_enrichi
                    }, timeout=30)

                    total += 1
                    if response.status_code == 200:
                        succes += 1
                        print(f"  ✅ {chemin_relatif}{partie}")
                    else:
                        print(f"  ⚠️  {chemin_relatif} — Erreur {response.status_code}: {response.text[:80]}")

                    time.sleep(0.2)

            except Exception as e:
                print(f"  ❌ Erreur lecture {fichier}: {e}")

    if nettoyer_apres:
        shutil.rmtree(chemin_projet, ignore_errors=True)
        print("\n🗑️  Dossier temporaire supprimé.")

    print("\n" + "="*60)
    print(f"📊 RÉSULTAT D'INGESTION — {project_id}")
    print(f"   ✅ {succes}/{total} fichiers envoyés avec succès")
    print(f"   ⏭️  {ignores} fichiers trop courts ignorés")
    print(f"\n💡 PROCHAINE ÉTAPE :")
    print(f"   Allez dans le Cerveau de votre tableau de bord AgentOps")
    print(f"   et validez les chunks PROPOSED → TRUSTED pour que l'IA")
    print(f"   les utilise dans ses réponses.")
    print(f"\n🔗 https://agentop-wechat-frontend.vercel.app")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    source = sys.argv[1]
    project_id = sys.argv[2]

    # Détection automatique : URL Git ou dossier local ?
    est_git = source.startswith("http://") or source.startswith("https://") or source.startswith("git@")

    if est_git:
        chemin = cloner_depuis_git(source)
        scanner_et_envoyer(chemin, project_id, nettoyer_apres=True)
    else:
        if not os.path.isdir(source):
            print(f"❌ Dossier introuvable : {source}")
            sys.exit(1)
        scanner_et_envoyer(source, project_id, nettoyer_apres=False)
