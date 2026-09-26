import os
import requests
import json
import time

repo_path = "/home/pmt/Téléchargements/mp-afritrips (1)/mp-afritrips/repo1"
EXTENSIONS_AUTORISEES = {".wxml", ".wxss", ".wxs", ".js", ".ts", ".json"}
DOSSIERS_IGNORES = {"node_modules", ".git", ".venv", "__pycache__", "dist", "build", "miniprogram_npm"}
API_URL = "https://wechat-agent-5y0i.onrender.com/api/v1/memory/learn"

print(f"🧠 Début de l'analyse du projet local (Branche: develop)")

success = 0
ignores = 0

for racine, dossiers, fichiers in os.walk(repo_path):
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
            
            if len(contenu.strip()) < 50:
                ignores += 1
                continue
            
            # Découper intelligemment en fragments pour ne pas surcharger l'API (max 2000 chars)
            chunks = [contenu[i:i+2000] for i in range(0, len(contenu), 2000)]
            
            for i, chunk in enumerate(chunks):
                texte = f"# Fichier: {chemin_relatif} (partie {i+1})\n\n{chunk}"
                
                payload = {
                    "project_id": "mp-afritrips",
                    "diff_content": texte
                }
                
                # Envoi au serveur Render
                res = requests.post(API_URL, json=payload)
                if res.status_code == 200:
                    success += 1
                    print(f"✅ Appris : {chemin_relatif} (chunk {i+1})")
                else:
                    print(f"❌ Erreur sur {chemin_relatif}: {res.text}")
                
                # Pause légère pour ne pas saturer le serveur Render
                time.sleep(0.5)
                
            # Pour la démo, on s'arrête à 15 morceaux pour être rapide et prouver le concept
            if success >= 15:
                break
                
        except Exception as e:
            pass
            
    if success >= 15:
        break

print(f"\n🎉 Entraînement terminé ! {success} blocs WXML/WXSS/JS de votre code local ont été injectés dans l'IA.")
