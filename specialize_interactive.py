import re

with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

# On ajoute la règle d'interaction à la fin des RÈGLES D'OR
addition = """
5. GESTION DE LA DUPLICATION (TRÈS IMPORTANT) :
   Ne génère jamais tout le code (API + UI) aveuglément si la demande est vague. 
   Si le développeur demande "Fais un écran", tu DOIS d'abord lui poser une question pour clarifier et éviter la duplication de code :
   - "As-tu besoin uniquement de l'UI (avec des données mockées) ?"
   - "As-tu déjà l'UI et tu as seulement besoin de l'API (Les 3 pièces) ?"
   - "Ou as-tu besoin de la page complète (UI + API) ?"
   Adapte ensuite ta réponse stricte uniquement à ce qu'il demande.
"""

# On insère cette règle juste avant "Si la question n'est pas liée..."
content = content.replace("Si la question n'est pas liée à WeChat", addition + "\nSi la question n'est pas liée à WeChat")

with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
    f.write(content)
