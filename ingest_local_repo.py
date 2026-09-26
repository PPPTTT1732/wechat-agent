import os
import sys
from packages.database.session import SessionLocal
from packages.database.sonatel_models import MemoryChunk

repo_path = "/home/pmt/Téléchargements/mp-afritrips (1)/mp-afritrips/repo1"
EXTENSIONS_AUTORISEES = {".py", ".js", ".ts", ".tsx", ".jsx", ".wxml", ".wxss", ".wxs", ".json", ".md", ".scss"}
DOSSIERS_IGNORES = {"node_modules", ".git", ".venv", "__pycache__", "dist", "build", "miniprogram_npm"}

db = SessionLocal()
success = 0
ignores = 0

print(f"🧠 Début de l'analyse du projet local : {repo_path}")

try:
    for racine, dossiers, fichiers in os.walk(repo_path):
        # Ignorer les dossiers non pertinents
        dossiers[:] = [d for d in dossiers if d not in DOSSIERS_IGNORES]
        for fichier in fichiers:
            _, ext = os.path.splitext(fichier)
            if ext not in EXTENSIONS_AUTORISEES:
                continue
            
            chemin_complet = os.path.join(racine, fichier)
            chemin_relatif = os.path.relpath(chemin_complet, repo_path)
            
            try:
                with open(chemin_complet, "r", encoding="utf-8", errors="ignore") as f:
                    contenu = f.read()
                
                # Ignorer les tout petits fichiers
                if len(contenu.strip()) < 50:
                    ignores += 1
                    continue
                
                # Découper intelligemment en fragments (chunks)
                chunks = [contenu[i:i+3000] for i in range(0, len(contenu), 3000)]
                
                for chunk in chunks:
                    texte = f"# Fichier: {chemin_relatif}\n\n{chunk}"
                    db_chunk = MemoryChunk(
                        project_id="mp-afritrips",
                        content=texte,
                        metadata_json={"source": "GitLab/Sonatel (Local)", "file": chemin_relatif, "branch": "develop"},
                        status="PROPOSED"
                    )
                    db.add(db_chunk)
                    success += 1
                    
            except Exception as e:
                pass
                
    db.commit()
    print(f"✅ Analyse terminée ! {success} blocs de code insérés dans le Cerveau de l'IA (Neon DB).")
    print(f"⏩ {ignores} petits fichiers ignorés.")
except Exception as e:
    print(f"Erreur : {e}")
finally:
    db.close()
