import re

with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

# On ajoute la règle 6 : Analyse de l'existant
addition = """
6. ANALYSE DE L'EXISTANT AVANT TOUTE ACTION (RÈGLE ABSOLUE) :
   Tu ne dois JAMAIS générer ou modifier du code à l'aveugle. 
   Avant de modifier une page, tu DOIS te bloquer et répondre :
   "Avant de faire quoi que ce soit, peux-tu me copier-coller ton code existant (WXML et JS) ? Je dois l'analyser pour m'y adapter sans casser ton architecture actuelle."
"""

# Insertion juste avant "CONTEXTE LOCAL WECHAT :"
content = content.replace("CONTEXTE LOCAL WECHAT :", addition + "\nCONTEXTE LOCAL WECHAT :")

with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
    f.write(content)
