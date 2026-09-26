import requests

BASE_URL = "https://wechat-agent-5y0i.onrender.com/api/v1"
PROJECT = "mp-afritrips"

print("1. Ajout du Skill strict (Directives P0/P1)...")
requests.post(f"{BASE_URL}/memory/skills", json={
    "title": "🚨 RÈGLES STRICTES RESPONSIVE (Suite Audit iOS)",
    "description": "INTERDICTION FORMELLE : 1) 'height: 100vh' + 'overflow: hidden' sur le layout. 2) Les hauteurs fixes sur les cards/conteneurs (utiliser min-height). 3) Les valeurs rpx à virgule (ex: 31.98rpx). 4) Le WXSS imbriqué type SCSS. OBLIGATOIRE : 1) Gérer l'encoche iPhone avec env(safe-area-inset-bottom). 2) box-sizing: border-box si padding horizontal. 3) Paddings bas dynamiques pour le tabbar.",
    "author": "Tech Lead"
})

print("2. Ingestion du document complet dans la mémoire RAG...")
# Pour cet exemple, on simule l'ingestion du texte reçu par l'utilisateur
audit_text = """
# DOCUMENT DE RÉFÉRENCE : Audit Responsive iPhone Reel
Le layout principal force la hauteur à 100vh et masque tout ce qui dépasse. Les pages doivent réserver l'espace bas avec env(safe-area-inset-bottom).
Les valeurs fractionnaires (ex: 31.98rpx) créent des gaps réels. Le nesting WXSS est invalide.
Priorités : Remplacer height par min-height. Supprimer overflow: hidden. Centraliser les safe areas.
"""
requests.post(f"{BASE_URL}/memory/learn", json={
    "project_id": PROJECT,
    "diff_content": audit_text
})

print("3. Validation immédiate (Lead Dev)...")
res = requests.get(f"{BASE_URL}/memory/review?project_id={PROJECT}")
for chunk in res.json():
    if "Audit Responsive" in chunk['content']:
        requests.post(f"{BASE_URL}/memory/review/{chunk['id']}", json={"status": "TRUSTED"})

print("✅ L'IA a assimilé l'audit iOS !")
