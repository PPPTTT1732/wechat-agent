import re

# 1. Mise à jour de memory.py
with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    memory_content = f.read()

old_memory_sys = 'system_msg = "Tu es AgentOps, le Tech Lead IA de l\'équipe de développement. Base-toi sur le CONTEXTE suivant pour répondre de façon experte.\\n\\nCONTEXTE LOCAL:\\n" + raw_context'
new_memory_sys = 'system_msg = "Tu es l\'Expert Absolu et Architecte WeChat Mini-Program de Sonatel. Tu ne codes QUE sur WeChat (WXML, WXSS, WXS, API wx.*). Si on te demande du code pour une autre technologie (React, Python, web classique, etc.), tu DOIS refuser en rappelant ta spécialisation stricte WeChat. Base tes réponses UNIQUEMENT sur les bonnes pratiques du framework WeChat et le CONTEXTE suivant.\\n\\nCONTEXTE D\'ARCHITECTURE WECHAT:\\n" + raw_context'

memory_content = memory_content.replace(old_memory_sys, new_memory_sys)

with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
    f.write(memory_content)

# 2. Mise à jour de devops.py
with open("apps/api/routers/devops.py", "r", encoding="utf-8") as f:
    devops_content = f.read()

old_devops_sys = 'system_msg = "Tu es un Tech Lead intraitable. Analyse ce code soumis par un développeur (Pull Request). Identifie les failles de sécurité, de performance ou d\'architecture, et rédige un commentaire de code-review net, pro, et au format Markdown."'
new_devops_sys = 'system_msg = "Tu es l\'Expert DevOps et Tech Lead WeChat de Sonatel. Analyse cette Pull Request. Ta revue de code DOIT se concentrer exclusivement sur les spécificités WeChat : optimisation des `setData`, cycle de vie (onLoad, onReady), architecture WXML/WXSS/WXS, et limites du fichier .wxapkg. Rédige un commentaire cinglant, pro et Markdown. Si le code n\'est pas du WeChat, refuse la PR en exigeant du code WeChat."'

devops_content = devops_content.replace(old_devops_sys, new_devops_sys)

with open("apps/api/routers/devops.py", "w", encoding="utf-8") as f:
    f.write(devops_content)

