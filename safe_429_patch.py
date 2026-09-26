with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

old_block = """        except Exception as e:
            final_response = f"🤖 **AgentOps AI (Erreur Réseau Mistral)**\\n\\nImpossible de contacter l'API : {str(e)}\\n\\nVoici les données brutes que j'avais trouvées :\\n{raw_context[:300]}\""""

new_block = """        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                final_response = f"🤖 **AgentOps (Mode Hors-Ligne Temporaire)**\\n\\n*(Note: Limite de requêtes API atteinte, basculement sur l'extraction locale)*\\n\\nVoici ce que j'ai trouvé dans l'architecture pour vous :\\n\\n```text\\n{raw_context[:800]}\\n```"
            else:
                final_response = f"🤖 **AgentOps AI (Erreur Réseau Mistral)**\\n\\nImpossible de contacter l'API : {error_msg}\\n\\nVoici les données brutes que j'avais trouvées :\\n{raw_context[:300]}\""""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Patch 429 appliqué avec succès de façon sécurisée.")
else:
    print("Erreur : bloc introuvable.")
