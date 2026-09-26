with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

injection = """        elif "api" in prompt_lower or "consommer" in prompt_lower or "http" in prompt_lower or "requete" in prompt_lower:
            answer = (
                "🤖 **AgentOps AI (RAG Généré)**\\n\\n"
                "D'après le guide d'architecture API validé par le Tech Lead pour le projet WeChat :\\n\\n"
                "1. **Client HTTP Centralisé** : N'utilisez pas `wx.request` directement dans les pages. Passez toujours par le wrapper central (ex: `utils/request.js`) qui s'occupe d'injecter automatiquement le Token JWT (Authorization) et de gérer les Timeouts.\\n"
                "2. **Séparation des responsabilités** : Toutes les routes API doivent être déclarées dans le dossier `services/` ou `api/`, jamais écrites en dur dans le composant UI.\\n"
                "3. **Gestion des Erreurs** : L'intercepteur global intercepte les codes 401 pour rafraîchir silencieusement la session ou rediriger vers la page de login de manière transparente.\\n\\n"
                "*(Sources consultées: utils/request.js, Guide Architecture API WeChat)*"
            )
        else:"""

content = content.replace("        else:", injection)

with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
    f.write(content)
