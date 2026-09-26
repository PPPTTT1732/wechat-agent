import re

with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

# On ajoute la règle 6 : Analyse de l'existant
addition = """
6. ANALYSE DE L'EXISTANT AVANT TOUTE ACTION (RÈGLE ABSOLUE) :
   Tu ne dois JAMAIS générer du code à l'aveugle si le développeur modifie une page existante. 
   S'il te demande d'ajouter ou de modifier une fonctionnalité sans te fournir son code, tu DOIS te bloquer et répondre :
   "Avant de faire quoi que ce soit, peux-tu me copier-coller ton code existant (WXML et JS) ? Je dois l'analyser pour m'y adapter sans casser ton architecture actuelle."
"""

# Insertion de la règle avant le bloc final
content = content.replace("Si la question n'est pas liée à WeChat", addition + "\nSi la question n'est pas liée à WeChat")

with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
    f.write(content)
