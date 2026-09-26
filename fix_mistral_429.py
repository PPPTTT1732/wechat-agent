import re

with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

new_except = """except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                final_response = f"🤖 **AgentOps (Mode Hors-Ligne Temporaire)**\\n\\n*(Note: Limite de requêtes API atteinte, basculement sur l'extraction locale)*\\n\\nVoici ce que j'ai trouvé dans l'architecture pour vous :\\n\\n```text\\n{raw_context[:800]}\\n```"
            else:
                final_response = f"🤖 **AgentOps AI (Erreur Réseau Mistral)**\\n\\nImpossible de contacter l'API : {error_msg}\\n\\nVoici les données brutes que j'avais trouvées :\\n{raw_context[:300]}\""""

pattern = re.compile(r'except Exception as e:.*?return \{"context": final_response\}', re.DOTALL)
replacement = new_except + '\n\n        return {"context": final_response}'

if pattern.search(content):
    content = pattern.sub(replacement, content)
    with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Sécurité 429 ajoutée avec succès.")
else:
    print("Pattern non trouvé.")
